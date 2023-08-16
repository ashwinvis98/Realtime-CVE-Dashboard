from web.db import db, BaseDocument, DataType
from datetime import datetime, timedelta
from web import bcrypt

MIN_DATE = datetime(2008, 1, 1)
MAX_DATE = datetime.now()


class CVE(BaseDocument):
    collection = db.cve
    fields = {
        "cve_id": DataType(str, nullable=False),
        "pub_date": DataType(datetime, nullable=False),
        "mod_date": DataType(datetime, nullable=False),
        "cvss": DataType(float, nullable=False),
        "cwe_code": DataType(int, nullable=False),
        "cwe_name": DataType(str, nullable=False),
        "summary": DataType(str, nullable=False),
        "access_vector": DataType(str, nullable=False),
        "access_complexity": DataType(str, nullable=False),
        "access_authentication": DataType(str, nullable=False),
        "impact_availability": DataType(str, nullable=False),
        "impact_confidentiality": DataType(str, nullable=False),
        "impact_integrity": DataType(str, nullable=False)
    }

    @classmethod
    def get_threat_proliferation(cls, min_date, max_date, bin_size):
        date_format = cls.get_bin_aggregate_date_format(bin_size)
        cves = cls.collection.aggregate([
            {"$match": {"pub_date": {"$gte": min_date, "$lte": max_date}}},
            {"$project": {"pub_date": 1}},
            {"$group": {
                "_id": {
                    "date": {"$dateToString": {"format": date_format, "date": "$pub_date"}}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.date": 1}}
        ])
        return cls.collect_data_by_bin(list(cves), min_date, max_date, bin_size, use_field=False)

    @classmethod
    def get_top_cves(cls, min_date, max_date, page, page_size, as_dicts=True):
        cves = cls.collection.aggregate([
            {"$match": {"pub_date": {"$gte": min_date, "$lte": max_date}}},
            {"$sort": {"cvss": -1}},
            {"$skip": page * page_size},
            {"$limit": page_size}
        ])
        return list(cves) if as_dicts else [cls(cve) for cve in cves]

    @classmethod
    def get_binned_by_field(cls, field, min_date, max_date, bin_size):
        date_format = cls.get_bin_aggregate_date_format(bin_size)
        cves = cls.collection.aggregate([
            {"$match": {"pub_date": {"$gte": min_date, "$lte": max_date}}},
            {"$project": {"pub_date": 1, field: 1}},
            {"$group": {
                "_id": {
                    "field": "$" + field,
                    "date": {"$dateToString": {"format": date_format, "date": "$pub_date"}}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.date": 1}}
        ])
        data = cls.collect_data_by_bin(list(cves), min_date, max_date, bin_size)
        return data

    @classmethod
    def collect_data_by_bin(cls, cves, min_date, max_date, bin_size, use_field=True):
        data = []
        date_format = cls.get_bin_aggregate_date_format(bin_size)
        current_date = min_date.replace(day=1)
        while current_date <= max_date:
            data_date = current_date.strftime(date_format)
            current_bin = {"date": current_date.strftime("%Y-%m-%d")}
            for cve in cves:
                if not use_field and cve["_id"]["date"] == data_date:
                    current_bin["count"] = cve["count"]
                elif cve["_id"]["date"] == data_date and cve["_id"].get("field"):
                    current_bin[cve["_id"]["field"]] = cve["count"]
            data.append(current_bin)
            current_date = cls.get_next_bin_date(current_date, bin_size)
        return data

    @classmethod
    def get_bin_aggregate_date_format(cls, bin_size):
        if bin_size == "month":
            return "%Y-%m"
        else:  # bin_size == "year"
            return "%Y"

    @classmethod
    def get_next_bin_date(cls, current_date, bin_size):
        if bin_size == "year":
            return current_date.replace(year=current_date.year + 1, day=1)
        else:  # bin_size == "month"
            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_year = current_date.year + 1 if next_month == 1 else current_date.year
            return current_date.replace(year=next_year, month=next_month, day=1)

    @classmethod
    def get_vulnerability_types(cls):
        return cls.collection.distinct("cwe_code")

    @classmethod
    def get_top_vulnerability_types(cls, min_date, page, page_size):
        pipeline = [
            {"$match": {"cwe_code": {"$exists": True, "$ne": -1}, "pub_date": {"$gte": min_date}}},
            {"$group": {
                "_id": "$cwe_code",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$skip": page * page_size},
            {"$limit": page_size},
            {"$project": {
                "_id": 0,
                "cwe_code": "$_id",
                "count": 1
            }}
        ]
        data = list(cls.collection.aggregate(pipeline))
        return data

    @classmethod
    def get_cwe_code_history(cls, cwe_codes, min_year, max_year):
        pipeline = get_history_pipeline(cwe_codes, min_year, max_year, collection_type="cwe")
        cwe_history = list(cls.collection.aggregate(pipeline))
        return format_history_data(cwe_history, date_field="pub_date")


class Product(BaseDocument):
    collection = db.products
    fields = {
        "cve_id": DataType(str, nullable=False),
        "year": DataType(int, nullable=False),
        "vulnerable_product": DataType(str, nullable=False)
    }

    @classmethod
    def get_top_products(cls, min_year, page, page_size, as_dicts=True):
        """Get the top products by number of CVEs in a given date range. Since the date of a CVE is in the CVE
        collection, this method uses an aggregate query to join the CVE and Product collections."""

        pipeline = [
            {"$match": {
                "vulnerable_product": {"$exists": True},
                "year": {"$gte": min_year}
            }},
            {"$group": {
                "_id": "$vulnerable_product",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$skip": page * page_size},
            {"$limit": page_size},
            {"$project": {
                "_id": 0,
                "product": "$_id",
                "count": 1
            }}
        ]

        products = cls.collection.aggregate(pipeline)
        return list(products) if as_dicts else [cls(product) for product in products]

    @classmethod
    def get_unique_products(cls):
        """Get the unique products in the Product collection."""
        products = cls.collection.aggregate([
            {"$group": {
                "_id": "$vulnerable_product"
            }},
            {"$project": {
                "_id": 0,
                "product": "$_id"
            }}
        ])
        return [product["product"] for product in products]

    @classmethod
    def get_product_history(cls, products, min_year, max_year):
        """Given a list of products, return the number of CVEs for each product in each year."""
        pipeline = get_history_pipeline(products, min_year, max_year)
        product_history = list(cls.collection.aggregate(pipeline))
        return format_history_data(product_history)


class VendorProduct(BaseDocument):
    collection = db.vendor_products
    fields = {
        "vendor": DataType(str, nullable=False),
        "product": DataType(str, nullable=False)
    }


class Vendor(BaseDocument):
    collection = db.vendors
    fields = {
        "cve_id": DataType(str, nullable=False),
        "year": DataType(int, nullable=False),
        "vendor": DataType(str, nullable=False)
    }

    @classmethod
    def get_top_vendors(cls, min_year, page, page_size, as_dicts=True):
        """Get the top vendors by number of CVEs in a given date range. Since the date of a CVE is in the CVE
        collection, this method uses an aggregate query to join the CVE and Vendor collections."""

        pipeline = [
            {"$match": {
                "vendor": {"$exists": True},
                "year": {"$gte": min_year}
            }},
            {"$group": {
                "_id": "$vendor",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$skip": page * page_size},
            {"$limit": page_size},
            {"$project": {
                "_id": 0,
                "vendor": "$_id",
                "count": 1
            }}
        ]

        vendors = Vendor.collection.aggregate(pipeline)
        return list(vendors) if as_dicts else [cls(vendor) for vendor in vendors]

    @classmethod
    def get_unique_vendors(cls):
        """Get the unique vendors in the Vendor collection."""
        vendors = cls.collection.aggregate([
            {"$group": {
                "_id": "$vendor"
            }},
            {"$project": {
                "_id": 0,
                "vendor": "$_id"
            }}
        ])
        return [vendor["vendor"] for vendor in vendors]

    @classmethod
    def get_vendor_history(cls, vendors, min_year, max_year):
        """Given a list of vendors, return the number of CVEs for each vendor in each year."""
        pipeline = get_history_pipeline(vendors, min_year, max_year, collection_type="vendor")
        vendor_history = list(cls.collection.aggregate(pipeline))
        return format_history_data(vendor_history)


def get_history_pipeline(items, min_date, max_date, collection_type="product"):
    """Given a list of products or vendors, return the number of CVEs for each product or vendor in each year."""
    if collection_type == "product":
        field = "vulnerable_product"
        date_field = "year"
    elif collection_type == "vendor":
        field = "vendor"
        date_field = "year"
    elif collection_type == "cwe":
        field = "cwe_code"
        date_field = "pub_date"
    else:
        raise ValueError("Invalid collection type: {}".format(collection_type))
    pipeline = [
        {"$match": {
            field: {"$in": items},
            date_field: {"$gte": min_date, "$lte": max_date}
        }},
        {"$group": {
            "_id": {
                "item": f"${field}",
                date_field: f"${date_field}" if collection_type != "cwe" else
                {"$dateToString": {"format": "%Y", "date": "$pub_date"}}
            },
            "count": {"$sum": 1}
        }},

        # group by year to get a list of products for each year
        {"$group": {
            "_id": f"$_id.{date_field}",
            "items": {"$push": {
                "item": "$_id.item",
                "count": "$count"
            }}
        }},
        {"$sort": {"_id": 1}},
        {"$project": {
            "_id": 0,
            date_field: "$_id",
            "items": 1
        }}
    ]

    return pipeline


def format_history_data(data, date_field="year"):
    """Given a list of products or vendors, return the number of CVEs for each product or vendor in each year."""
    formatted = []
    for year_block in data:
        new_year_block = {"date": year_block[date_field]}
        for item in year_block["items"]:
            if item["item"]:
                new_year_block[item["item"]] = item["count"]
        formatted.append(new_year_block)
    return formatted


class User(BaseDocument):
    collection = db.users
    fields = {
        "email": DataType(str, nullable=False),
        "name": DataType(str, nullable=False),
        "password": DataType(str, nullable=False),
        "subscribed": DataType(bool, nullable=False, default=False),
    }

    def get_id(self):
        # For login management purposes only - do not remove
        return str(self["_id"])

    @staticmethod
    def login(email, password):
        user = User.find(search={"email": email}, one=True)

        if not user:
            print(f"User with email {email} does not exist")
            return None

        if bcrypt.check_password_hash(user["password"], password):
            print(f"User with email {email} logged in successfully")
            return user

        print(f"Invalid password for user with email {email}")
        return None

    @staticmethod
    def create(email, name, password, push=True):
        if User.find(search={"email": email}, one=True):
            print(f"User with email {email} already exists")
            return None

        user = User({
            "email": email,
            "password": bcrypt.generate_password_hash(password).decode('utf-8'),
            "name": name
        })
        if push:
            user.push()
            print(f"User with email {email} created successfully")
        return user


def test():
    from pymongo import UpdateOne
    # Aggregate the relevant Product documents
    pipeline = [
        {"$group": {"_id": "$cve_id", "products": {"$push": "$vulnerable_product"}}}
    ]
    product_aggregation = Product.collection.aggregate(pipeline)

    # Create a list of bulk write operations to update the corresponding CVE documents
    bulk_operations = []
    for product_doc in product_aggregation:
        cve_id = product_doc["_id"]
        products = product_doc["products"]
        bulk_operations.append(UpdateOne({"cve_id": cve_id}, {"$set": {"products": products}}))

    # Execute the bulk write operations
    result = CVE.collection.bulk_write(bulk_operations)
    print(f"{result.modified_count} documents updated")


if __name__ == "__main__":
    test()
