from web import app
import math
import json
import contextlib
from copy import deepcopy
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from datetime import datetime
import certifi

ca = certifi.where()
client = MongoClient(app.config["MONGO_URI"], tlsCAFile=ca)
db = client[app.config["MONGO_DB"]]
SESSION = None


@contextlib.contextmanager
def transaction():
    with client.start_session() as session:
        with session.start_transaction():
            global SESSION
            SESSION = session
            yield
            SESSION = None


def get_obj_id(obj_id):
    if isinstance(obj_id, str):
        try:
            return ObjectId(obj_id)
        except InvalidId:
            return None
    return obj_id


class DataTypeError(RuntimeError):
    pass


class DBError(RuntimeError):
    pass


class DataType:
    def __init__(self, data_type, nullable=True, default=None, choices=()):
        self.data_type = data_type
        self.nullable = nullable
        self.choices = choices
        self.default = default

    def enforce(self, value):
        if value is None and self.nullable:
            return True
        if value is None and not self.nullable:
            return False
        if not isinstance(value, self.data_type):
            return False
        if self.choices and value not in self.choices:
            return False
        return True

    def conform(self, value):
        if value is None:
            return deepcopy(self.default)
        return value


class AnyType(DataType):
    def __init__(self, nullable=True, default=None, choices=()):
        super().__init__(object, nullable=nullable, default=default, choices=choices)


class ListType(DataType):

    def __init__(self, data_type, nullable=True, default=None, choices=()):
        assert isinstance(data_type, DataType)
        super().__init__(data_type, nullable=nullable, default=default, choices=choices)

    def enforce(self, value):
        if value is None and self.nullable:
            return True
        if not isinstance(value, list):
            return False

        for item in value:
            if not self.data_type.enforce(item):
                return False
            if self.choices and item not in self.choices:
                return False
        return True


class DictType(DataType):
    def __init__(self, data_type=None, nullable=True, default=None):
        if not data_type:
            data_type = AnyType()

        elif isinstance(data_type, DataType):
            pass

        elif isinstance(data_type, dict):
            for value in data_type.values():
                if not isinstance(value, DataType):
                    raise DataTypeError(f"Invalid data type: {data_type}")

        else:
            raise DataTypeError(f"Invalid data type: {data_type}")

        super().__init__(data_type, nullable=nullable, default=default)

    def enforce(self, value):
        if value is None and self.nullable:
            return True
        if not isinstance(value, dict):
            return False

        if isinstance(self.data_type, dict):
            for key, item in value.items():
                if key not in self.data_type:
                    return False
                if not self.data_type[key].enforce(item):
                    return False
        else:
            for item in value.values():
                if not self.data_type.enforce(item):
                    return False

        return True


ID_TYPE = DataType(ObjectId, nullable=False)


class ReferenceType(DataType):
    def __init__(self, collection=None, nullable=True):
        super().__init__(collection, nullable=nullable)

    def enforce(self, value):
        if value is None and self.nullable:
            return True
        if isinstance(value, BaseDocument) and value["_id"]:
            return True
        if ID_TYPE.enforce(get_obj_id(value)):
            return True
        return False

    def conform(self, value):
        if isinstance(value, BaseDocument):
            return value["_id"]
        return get_obj_id(value)


class BaseDocument:
    collection = None
    fields = {}  # Add "*" to fields if the Document accepts ANY field (i.e. is freeform)

    def __init__(self, document, check_validity=True):
        if not isinstance(document, dict):
            raise DBError("Invalid document passed. Must be a dictionary.")

        self._document = {}
        self._orig_document = deepcopy(document)

        if check_validity:
            for field, value in document.items():
                self[field] = value
        else:
            self._document = document
        self.set_default()
        if check_validity:
            self.check_validity()

    def set_default(self):
        for field, data_type in self.fields.items():
            field_value = self._document.get(field)
            self._document[field] = data_type.conform(field_value)

    def check_validity(self):
        if self._document.get("_id") != self._orig_document.get("_id"):
            raise DBError("You cannot change the id of an existing database document. Use the .copy(reset_id=True) "
                          "and .delete() methods instead.")

        for field, value in self._document.items():
            if not self.field_is_valid(field, value):
                raise DBError(f"Document does not conform to specified fields or data types ({field}).")

        for field, data_type in self.fields.items():
            field_value = self._document.get(field)
            if not self.field_is_valid(field, field_value):
                raise DBError(f"Document does not conform to specified fields or data types ({field}).")

    @classmethod
    def field_is_valid(cls, field, value):
        if field == "_id":
            return ID_TYPE.enforce(value)
        elif field in cls.fields:
            data_type = cls.fields[field]
        elif "*" in cls.fields:
            data_type = cls.fields["*"]
        else:
            return False
        return data_type.enforce(value)

    @classmethod
    def field_is_defined(cls, field):
        if field == "_id":
            return True
        if field in cls.fields or "*" in cls.fields:
            return True
        return False

    @classmethod
    def get_field_data_type(cls, field):
        if field == "_id":
            return ID_TYPE
        elif field in cls.fields:
            return cls.fields[field]
        elif "*" in cls.fields:
            return cls.fields["*"]
        else:
            return None

    def get_data(self):
        return self._document

    def __getitem__(self, key):
        if not self.field_is_defined(key):
            raise DBError(f"The field '{key}' is not defined for this collection.")
        if key not in self._document:
            return None
        return self._document[key]

    def __setitem__(self, key, value):
        if key == "_id":
            value = get_obj_id(value)
        if not self.field_is_valid(key, value):
            raise DBError(f"Could not set '{key}'='{value}'. Either the field is not defined or the value is not the "
                          f"correct data type.")
        self._document[key] = self.get_field_data_type(key).conform(value)

    def get(self, key, default=None):
        try:
            return self[key]
        except DBError:
            return default

    @classmethod
    def from_id(cls, obj_id, check_validity=True):
        obj_id = get_obj_id(obj_id)
        document = cls.collection.find_one({"_id": obj_id}, session=SESSION)
        if document is None:
            return None
        return cls(document, check_validity=check_validity)

    @classmethod
    def create_many(cls, raw_documents, push=True):
        clean_documents = []
        if not raw_documents:
            return []
        for doc in raw_documents:
            clean_doc = cls(doc)
            clean_doc.check_validity()
            clean_documents.append(clean_doc.get_data())

        if push:
            results = cls.collection.insert_many(clean_documents, ordered=False, session=SESSION)
            for i, doc in enumerate(clean_documents):
                doc["_id"] = results.inserted_ids[i]

        def generator(docs):
            for inner_doc in docs:
                yield cls(inner_doc)
        return generator(clean_documents)

    def push(self, update_instructions=None, overwrite=False):
        self.check_validity()

        if self.is_on_db():

            if update_instructions:
                # https://docs.mongodb.com/manual/reference/method/db.collection.updateOne/
                self.collection.update_one({"_id": self._document["_id"]}, update_instructions, session=SESSION)

            elif overwrite:
                self.collection.replace_one({"_id": self._document["_id"]}, self._document, session=SESSION)
            else:
                update_data = self._get_update_data()
                if update_data:
                    self.collection.update_one({"_id": self._document["_id"]}, update_data, session=SESSION)

        else:
            self.collection.insert_one(self._document, session=SESSION)
        self._orig_document = deepcopy(self._document)

    def _get_update_data(self):
        update_data = {}
        set_data, unset_data = generate_differences(self._orig_document, self._document)
        if set_data:
            update_data["$set"] = set_data
        if unset_data:
            update_data["$unset"] = unset_data
        return update_data

    def pull(self):
        if self.is_on_db():
            self._document = self.collection.find_one({"_id": self._orig_document["_id"]}, session=SESSION)
            self._orig_document = deepcopy(self._document)
        else:
            raise DBError("Cannot pull from database. Document does not exist ('_id' not specified).")

    def delete(self):
        if self.is_on_db():
            self.collection.delete_one({"_id": self._document["_id"]}, session=SESSION)
        else:
            raise DBError("Cannot delete from database. Document does not exist ('_id' not specified).")

    def copy(self, reset_id=False):
        new_document = deepcopy(self._document)
        if reset_id and "_id" in new_document:
            del new_document["_id"]
        return self.__class__(new_document)

    def is_on_db(self):
        if not self._document.get("_id"):
            return False
        result = self.collection.find_one({"_id": self._document["_id"]}, {"_id": 1})
        return bool(result)

    def is_outdated(self):
        most_recent_db_document = self.collection.find_one({"_id": self._document["_id"]}, session=SESSION)
        return self._orig_document != most_recent_db_document

    @classmethod
    def exists_on_db(cls, search):
        if cls.collection.count_documents(search, session=SESSION) > 0:
            return True
        return False

    @classmethod
    def find(cls, search=None, projection=None, one=False, page=0, page_size=None, raw_result=False):
        if one:
            document = cls.collection.find_one(search, projection, session=SESSION)
            if document is None:
                return None
            return cls(document) if not raw_result else document
        else:
            documents = cls.collection.find(search, projection, session=SESSION)
            if page_size:
                documents.skip(page * page_size).limit(page_size)

            def generator():
                for doc in documents:
                    yield cls(doc) if not raw_result else doc
            return generator()

    @classmethod
    def count(cls, search=None):
        if not search:
            search = {}
        return cls.collection.count_documents(search, session=SESSION)

    @classmethod
    def count_pages(cls, page_size, search=None):
        num_documents = cls.count(search=search)
        return (num_documents // page_size) + 1

    def __repr__(self):
        return f"{self.__class__.__name__}(_id={self._document.get('_id')})"


def generate_differences(orig, new, path=""):
    if isinstance(orig, dict) and isinstance(new, dict):
        set_data = {}
        unset_data = {}
        for field in set(list(orig.keys()) + list(new.keys())):
            new_path = join_path(path, field)
            if field in orig and field in new:
                set_diff, unset_diff = generate_differences(orig[field], new[field], path=new_path)
                set_data.update(set_diff)
                unset_data.update(unset_diff)
            elif field not in orig:
                set_data[new_path] = new[field]
            else:  # field not in new
                unset_data[new_path] = ""
        return set_data, unset_data

    elif is_nan(orig) or is_nan(new):
        return generate_nan_differences(orig, new, path)
    elif orig != new:
        return {path: new}, {}
    return {}, {}


def generate_nan_differences(orig, new, path):
    # At least one parameter must be nan
    if is_nan(orig) and is_nan(new):
        return {}, {}
    else:
        return {path: new}, {}


def is_nan(value):
    if not isinstance(value, float):
        return False
    return math.isnan(value)


def join_path(path, field):
    if path == "":
        return f"{field}"
    else:
        return f"{path}.{field}"


def get_json_compatible(data):
    datatype = type(data)
    if datatype is list:
        return [get_json_compatible(item) for item in data]
    elif datatype is dict:
        return {field: get_json_compatible(value) for field, value in data.items()}
    elif datatype is ObjectId:
        return str(data)
    elif datatype is datetime:
        return data.isoformat()
    else:
        return data


def serialize(data):
    datatype = type(data)
    if datatype is not list and datatype is not dict:
        if datatype is ObjectId:
            serialized_data = {'type': 'ObjectId', 'value': str(data)}
        elif datatype is datetime:
            serialized_data = {'type': 'datetime', 'value': data.strftime('%m/%d/%Y, %H:%M:%S')}
        else:
            serialized_data = {'type': 'no_change', 'value': data}
    elif datatype is list:
        serialized_data = {'type': 'list', 'value': [serialize(item) for item in data]}
    else:
        serialized_data = {'type': 'dict', 'value': {field: serialize(value) for field, value in data.items()}}
    return json.dumps(serialized_data)


def deserialize(data):
    data = json.loads(data)
    if data['type'] != 'list' and data['type'] != 'dict':
        if data['type'] == 'ObjectId':
            return get_obj_id(data['value'])
        elif data['type'] == 'datetime':
            return datetime.strptime(data['value'], '%m/%d/%Y, %H:%M:%S')
        else:
            return data['value']
    elif data['type'] == 'list':
        return [deserialize(item) for item in data['value']]
    else:
        return dict({field: deserialize(value) for (field, value) in data['value'].items()})


def filter_documents(documents, query_fields):
    filtered = []
    for document in documents:
        matches = True
        for field, value in query_fields.items():
            if document.get(field) != value:
                matches = False
                break
        if matches:
            filtered.append(document)
    return filtered
