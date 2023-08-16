import os
import json

CWE_NAME_FILE = os.path.join(os.path.dirname(__file__), 'cwe_names.json')


def load_cwe_names():
    with open(CWE_NAME_FILE, 'r') as f:
        return json.load(f)


def cwe_codes_to_names(codes):
    cwe_names = load_cwe_names()
    new_items = []
    for code in codes:
        if str(code) in cwe_names:
            new_items.append(cwe_names[str(code)])
        else:
            new_items.append(f"CWE {code} (Unknown)")
    return new_items


def cwe_names_to_codes(names):
    cwe_names = load_cwe_names()
    new_items = []
    for name in names:
        for key, value in cwe_names.items():
            if value == name:
                new_items.append(int(key))
    return new_items


def replace_cwe_codes_with_names(items):
    cwe_names = load_cwe_names()
    new_items = []
    for item in items:
        new_item = {}
        for key, value in item.items():
            if key != "date":
                if str(key) in cwe_names:
                    name = cwe_names[str(key)]
                else:
                    name = f"CWE {key} (Unknown)"
                new_item[name] = new_item.get(name, 0) + value
            else:
                new_item[key] = value
        new_items.append(new_item)
    return new_items


def replace_cwe_codes_with_names_count(items):
    cwe_names = load_cwe_names()
    new_items = []
    for item in items:
        new_item = {}
        for key, value in item.items():
            if key == "cwe_code":
                if str(value) in cwe_names:
                    new_item["cwe_name"] = cwe_names[str(value)]
                else:
                    new_item["cwe_name"] = f"CWE {value} (Unknown)"
            else:
                new_item[key] = value
        new_items.append(new_item)
    return new_items
