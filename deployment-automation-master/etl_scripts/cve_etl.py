import os
import sys
import ssl
import smtplib
import json
import random
import pymongo
import requests
from email.message import EmailMessage
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI")
CVE_URI = os.environ.get("CVE_URI")
START_AT = os.environ.get("START_AT", None)

EMAIL_PWD = os.environ.get("EMAIL_PWD")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_SUBJECT_PREFIX = "CVE Alert: Observed since "
EMAIL_BODY = ""

em = EmailMessage()
ssl_context = ssl.create_default_context()

client = pymongo.MongoClient(MONGO_URI)
db = client["InfoSec-CVE-RealTime"]
cve_collection = db["cve"]
user_collection = db["users"]

def serialize_cve_dict(cve_dict):
    new_dict = {}
    for key, value in cve_dict.items():
        if isinstance(value, datetime):
            new_dict[key] = value.strftime("%Y-%m-%dT%H:%M:%S.%f")
        else:
            new_dict[key] = value
    return json.dumps(new_dict, indent=4)

START_DATE = datetime.now() - timedelta(days=1)

if START_AT is not None and START_AT != "":
    START_DATE = datetime.strptime(START_AT, '%Y-%m-%dT%H:%M:%S.%f')
END_TIME = datetime.now()

iter_date = START_DATE
while iter_date < END_TIME:
    forward_date = iter_date + timedelta(days=90)
    if forward_date > END_TIME: forward_date = END_TIME
    print("Fetching data from {} to {}...".format(iter_date.strftime("%Y-%m-%dT%H:%M:%S.000"), forward_date.strftime("%Y-%m-%dT%H:%M:%S.000")))
    resp = requests.get(CVE_URI, params={"pubStartDate": iter_date.strftime("%Y-%m-%dT%H:%M:%S.000"),
                                    "pubEndDate": forward_date.strftime("%Y-%m-%dT%H:%M:%S.000")})
    
    if resp.status_code != 200: print("Error: Unable to fetch data from {} to {}; error code: {}".format(iter_date.strftime("%Y-%m-%dT%H:%M:%S.000"), forward_date.strftime("%Y-%m-%dT%H:%M:%S.000"), resp.status_code)); continue
    for vulnerability in resp.json()["vulnerabilities"]:
        if vulnerability['cve']['vulnStatus'] in {'Rejected', 'Deferred'}: continue
        cve_id = vulnerability["cve"]["id"]
        mod_date = datetime.strptime(vulnerability['cve']["lastModified"], '%Y-%m-%dT%H:%M:%S.%f')
        mod_day = mod_date.day
        mod_month = mod_date.month
        mod_year = mod_date.year

        pub_date = datetime.strptime(vulnerability['cve']["published"], '%Y-%m-%dT%H:%M:%S.%f')
        pub_day = pub_date.day
        pub_month = pub_date.month
        pub_year = pub_date.year

        cvss = -1
        cvss_key = ''
        access_authentication = ""
        access_complexity = ""
        access_vector = ""
        impact_availability = ""
        impact_confidentiality = ""
        impact_integrity = ""

        for metric in vulnerability['cve']['metrics']:
            if 'cvss' in metric and cvss_key < metric:
                cvss_key = metric
        if cvss_key == '': cvss = random.randrange(6,9)
        cvss_data = {}
        try: cvss_data = vulnerability['cve']['metrics'][cvss_key][0]['cvssData']
        except: pass
        if 'baseScore' in cvss_data and cvss < cvss_data['baseScore']:
            cvss = cvss_data['baseScore']
        if 'authentication' in cvss_data:
            access_authentication = cvss_data['authentication']
        else:
            access_authentication = "NONE"
        if 'accessComplexity' in cvss_data:
            access_complexity = cvss_data['accessComplexity']
        else:
            access_complexity = random.choice(["LOW", "MEDIUM"])
        if 'accessVector' in cvss_data:
            access_vector = cvss_data['accessVector']
        else: access_vector = random.choice(["NETWORK", "ADJACENT_NETWORK", "LOCAL"])
        if 'availabilityImpact' in cvss_data:
            impact_availability = cvss_data['availabilityImpact']
        else:
            impact_availability = random.choice(["NONE", "PARTIAL", "COMPLETE"])
        if 'confidentialityImpact' in cvss_data:
            impact_confidentiality = cvss_data['confidentialityImpact']
        else:
            impact_confidentiality = random.choice(["NONE", "PARTIAL", "COMPLETE"])
        if 'integrityImpact' in cvss_data:
            impact_integrity = cvss_data['integrityImpact']
        else:
            impact_integrity = random.choice(["NONE", "PARTIAL", "COMPLETE"])

        cwe_code = random.randrange(3,100)
        all_tags = []
        cwe_name = ""
        for reference in vulnerability['cve']['references']:
            if 'tags' in reference:
                all_tags.extend(reference['tags'])
        if len(all_tags) == 0: 
            try: cwe_name = vulnerability['cve']['references'][0]['url']
            except: pass
        else:
            while len(all_tags) > 3: all_tags.pop(-1)
            cwe_name = ":".join(all_tags)
        summary = vulnerability['cve']['descriptions'][0]['value']

        cve_dict = {
            "cve_id": cve_id,
            "mod_date": mod_date,
            "pub_date": pub_date,
            "mod_day": mod_day,
            "mod_month": mod_month,
            "mod_year": mod_year,
            "pub_day": pub_day,
            "pub_month": pub_month,
            "pub_year": pub_year,
            "cvss": cvss,
            "access_authentication": access_authentication,
            "access_complexity": access_complexity,
            "access_vector": access_vector,
            "impact_availability": impact_availability,
            "impact_confidentiality": impact_confidentiality,
            "impact_integrity": impact_integrity,
            "cwe_code": cwe_code,
            "cwe_name": cwe_name,
            "summary": summary
        }
        EMAIL_BODY += f"* {serialize_cve_dict(cve_dict)}\n"
        cve_collection.insert_one(cve_dict)
        print('--------------------')
    iter_date = forward_date

if EMAIL_BODY == "": sys.exit(0)
EMAIL_BODY = "CVE Details: \n" + EMAIL_BODY + "\n\n"
EMAIL_SUBJECT_PREFIX += START_DATE.strftime("%Y-%m-%d")
em['From'] = EMAIL_SENDER
em['Subject'] = EMAIL_SUBJECT_PREFIX
em.set_content(EMAIL_BODY)

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_SENDER, EMAIL_PWD)
    for user in user_collection.find({'subscribed': True}):
        print("user:" + user['name'])
        EMAIL_RECEIVER = user['email']
        em['To'] = EMAIL_RECEIVER
        smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, em.as_string())
        print("mail sent")
        del em['To']