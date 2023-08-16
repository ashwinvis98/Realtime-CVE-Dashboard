import os
import pymongo
import requests
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI")
CVE_URI = os.environ.get("CVE_URI")

client = pymongo.MongoClient(MONGO_URI)
db = client["InfoSec-CVE-RealTime"]
product_collection = db["products"]
vendor_collection = db["vendors"]


def find_vendor_product(data):
    data = data.split(":")
    product = data[4]
    vendor = data[-2] if data[-2] != "*" else data[-4]
    if vendor == "*": vendor = data[3]
    return vendor, product

def upload_vendor_product_to_db(cve_id, vendor, product):
    year = int(cve_id.split("-")[1])
    vendor_dict = {"vendor": vendor, "cve_id": cve_id, "year": year}
    product_dict = {"vulnerable_product": product, "cve_id": cve_id, "year": year}
    vendor_collection.insert_one(vendor_dict)
    product_collection.insert_one(product_dict)

if __name__ == "__main__":
    start_date = datetime(2021, 1, 1)
    cur_date = datetime.now()
    iter_date = start_date
    products_written = 0
    while iter_date < cur_date:
        forward_date = iter_date + timedelta(days=90)
        print("Fetching data from {} to {}...".format(iter_date.strftime("%Y-%m-%dT%H:%M:%S.000"), forward_date.strftime("%Y-%m-%dT%H:%M:%S.000")))
        resp = requests.get(CVE_URI, params={"pubStartDate": iter_date.strftime("%Y-%m-%dT%H:%M:%S.000"),
                                        "pubEndDate": forward_date.strftime("%Y-%m-%dT%H:%M:%S.000")})
        
        if resp.status_code != 200: print("Error: Unable to fetch data from {} to {}; error code: {}".format(iter_date.strftime("%Y-%m-%dT%H:%M:%S.000"), forward_date.strftime("%Y-%m-%dT%H:%M:%S.000"), resp.status_code)); continue
        for vulnerability in resp.json()["vulnerabilities"]:
            cve_id = vulnerability["cve"]["id"]
            try: 
                cpe_data = vulnerability["cve"]["configurations"][0]['nodes'][0]['cpeMatch'][0]['criteria']
                vendor, product = find_vendor_product(cpe_data)
                upload_vendor_product_to_db(cve_id, vendor, product)
                products_written += 1
            except Exception as e: print("No cpe_data for cve_id", cve_id); print('products written:', products_written); continue
        iter_date = forward_date