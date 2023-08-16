import flask
from flask_cors import cross_origin
import traceback
from web import app
from datetime import datetime, timedelta
from web.models import CVE, Product, MIN_DATE, MAX_DATE, User, Vendor
from web.db import get_json_compatible
from web.cwe_names.replace_cwe_codes_with_names import replace_cwe_codes_with_names, replace_cwe_codes_with_names_count,\
    cwe_codes_to_names, cwe_names_to_codes


@app.route("/")
@cross_origin()
def home():
    return flask.jsonify({"message": "Hello World!"})


@app.route("/api/v1.0/signup", methods=["POST"])
@cross_origin()
def signup():
    data = flask.request.get_json()
    # print(data)
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")
    print()
    if not email or not password:
        return flask.jsonify({"message": "Email, name, and password are required."}), 400
    try:
        user = User.create(email, name, password)
    except Exception:
        traceback.print_exc()
        return flask.jsonify({"message": "An error occurred while creating the user."}), 500
    if not user:
        return flask.jsonify({"message": "User with that email already exists."}), 400
    return flask.jsonify({
        "user": {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "subscribed": user["subscribed"]
        }
    }), 201


@app.route("/api/v1.0/login", methods=["POST"])
# @cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
@cross_origin()
def login():
    email = flask.request.json.get("email")
    password = flask.request.json.get("password")
    if not email or not password:
        return flask.jsonify({"message": "Email and password are required."}), 400
    user = User.login(email, password)
    if user is None:
        return flask.jsonify({"message": "Invalid email or password."}), 400
    response = flask.jsonify(
        {
            "user_id": str(user["_id"]),
            "email": email,
            "name": password,
            "subscribed": user["subscribed"]
        }
    )
    # response.headers.add("Access-Control-Allow-Origin", "*")
    # response.headers.add("Access-Control-Allow-Headers", "*")
    # response.headers.add("Access-Control-Allow-Methods", "*")
    return response, 200


@app.route("/api/v1.0/user_session", methods=["POST"])
@cross_origin()
def get_user_session():
    user_id = flask.request.json.get("user_id")
    if not user_id:
        return flask.jsonify({"message": "No user session found."}), 404
    user = User.from_id(user_id)
    if not user:
        return flask.jsonify({"message": "No user session found."}), 404
    return flask.jsonify({
        "user": {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "subscribed": user["subscribed"]
        }
    }), 200


@app.route("/api/v1.0/set_subscription", methods=["POST"])
@cross_origin()
def set_subscription():
    user_id = flask.request.json.get("user_id")
    subscribe = bool(flask.request.json.get("subscribe"))
    user = User.from_id(user_id)
    if not user:
        return flask.jsonify({"message": "No user session found."}), 404
    user["subscribed"] = subscribe
    user.push()
    return flask.jsonify({
        "user": {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "subscribed": user["subscribed"]
        }}), 200


@app.route("/api/v1.0/top_cves")  # API ROUTE 1
@cross_origin()
def top_cves():
    min_date, max_date = get_date_args()
    page, page_size = get_top_data_args()
    cves = CVE.get_top_cves(min_date, max_date, page, page_size)
    return flask.jsonify(get_json_compatible(cves))


@app.route("/api/v1.0/access_complexity")  # API ROUTE 2
@cross_origin()
def access_complexity():
    min_date, max_date = get_date_args()
    bin_size = get_arg("bin_size", default="year", choices=("month", "year"))
    data = CVE.get_binned_by_field("access_complexity", min_date, max_date, bin_size)
    return flask.jsonify(get_json_compatible(data))


@app.route("/api/v1.0/access_vector")  # API ROUTE 3
@cross_origin()
def access_vector():
    min_date, max_date = get_date_args()
    bin_size = get_arg("bin_size", default="year", choices=("month", "year"))
    data = CVE.get_binned_by_field("access_vector", min_date, max_date, bin_size)
    return flask.jsonify(get_json_compatible(data))


@app.route("/api/v1.0/top_products")  # API ROUTE 4
@cross_origin()
def top_products():
    min_year, _ = get_year_args()
    page, page_size = get_top_data_args()
    data = Product.get_top_products(min_year, page, page_size)
    return flask.jsonify(get_json_compatible(data))


@app.route("/api/v1.0/access_authentication")  # API ROUTE 5
@cross_origin()
def access_authentication():
    min_date = get_arg("min_date", default=MIN_DATE, coerce_type=datetime)
    max_date = get_arg("max_date", default=datetime.now(), coerce_type=datetime)
    bin_size = get_arg("bin_size", default="year", choices=("month", "year"))
    data = CVE.get_binned_by_field("access_authentication", min_date, max_date, bin_size)
    return flask.jsonify(get_json_compatible(data))


@app.route("/api/v1.0/impact_availability")  # API ROUTE 6
@cross_origin()
def impact_availability():
    min_date, max_date = get_date_args()
    bin_size = get_arg("bin_size", default="year", choices=("month", "year"))
    data = CVE.get_binned_by_field("impact_availability", min_date, max_date, bin_size)
    return flask.jsonify(get_json_compatible(data))


@app.route("/api/v1.0/vulnerability_types")  # API ROUTE 7
@cross_origin()
def get_vulnerability_types():
    vuln_types = CVE.get_vulnerability_types()
    vuln_types = list(set(cwe_codes_to_names(vuln_types)))
    top_10 = CVE.get_top_vulnerability_types(MIN_DATE, 0, 10)
    top_10 = replace_cwe_codes_with_names_count(top_10)
    top_names = []
    top = []
    for item in top_10:
        if len(top_names) == 5:
            break
        if item["cwe_name"] in top_names:
            continue
        top_names.append(item["cwe_name"])
        top.append({"cwe_name": item["cwe_name"], "count": item["count"]})
    top = [x["cwe_name"] for x in top]
    return flask.jsonify(get_json_compatible({"items": vuln_types, "top_items": top}))


@app.route("/api/v1.0/vulnerability_type_history")  # API ROUTE 7.5
@cross_origin()
def vulnerability_type():
    vulnerability_types = flask.request.args.get("items") or ""
    if not vulnerability_types:
        return flask.jsonify(get_json_compatible([]))
    vulnerability_types = vulnerability_types.split(",")
    cwe_codes = cwe_names_to_codes(vulnerability_types)
    data = CVE.get_cwe_code_history(cwe_codes, MIN_DATE, MAX_DATE)
    data = replace_cwe_codes_with_names(data)
    data = get_history_totals(vulnerability_types, data)
    return flask.jsonify(get_json_compatible(data))


@app.route("/api/v1.0/threat_proliferation")  # API ROUTE 8
@cross_origin()
def threat_proliferation():
    min_date, max_date = get_date_args()
    bin_size = get_arg("bin_size", default="month", choices=("month", "year"))
    data = CVE.get_threat_proliferation(min_date, max_date, bin_size)
    for block in data:
        if "count" not in block:
            block["count"] = 0
    return flask.jsonify(get_json_compatible(data))


@app.route("/api/v1.0/top_vendors")  # API ROUTE 9
@cross_origin()
def top_vendors():
    min_year, _ = get_year_args()
    page, page_size = get_top_data_args()
    data = Vendor.get_top_vendors(min_year, page, page_size)
    return flask.jsonify(get_json_compatible(data))


@app.route("/api/v1.0/get_products")  # API ROUTE 10
@cross_origin()
def get_products():
    products = Product.get_unique_products()
    top = Product.get_top_products(MIN_DATE.year, 0, 5)
    return flask.jsonify(get_json_compatible({"items": products, "top_items": [x["product"] for x in top]}))


@app.route("/api/v1.0/get_vendors")  # API ROUTE 11
@cross_origin()
def get_vendors():
    vendors = Vendor.get_unique_vendors()
    top = Vendor.get_top_vendors(MIN_DATE.year, 0, 5)
    return flask.jsonify(get_json_compatible({"items": vendors, "top_items": [x["vendor"] for x in top]}))


@app.route("/api/v1.0/product_history")  # API ROUTE 12
@cross_origin()
def product_history():
    products = flask.request.args.get("items") or ""
    if not products:
        return flask.jsonify(get_json_compatible([]))
    products = products.split(",")
    data = Product.get_product_history(products, MIN_DATE.year, MAX_DATE.year)
    data = get_history_totals(products, data)
    return flask.jsonify(get_json_compatible(data))


@app.route("/api/v1.0/vendor_history")  # API ROUTE 13
@cross_origin()
def vendor_history():
    vendors = flask.request.args.get("items") or ""
    if not vendors:
        return flask.jsonify(get_json_compatible([]))
    vendors = vendors.split(",")
    data = Vendor.get_vendor_history(vendors, MIN_DATE.year, MAX_DATE.year)
    data = get_history_totals(vendors, data)
    return flask.jsonify(get_json_compatible(data))


def get_history_totals(items, data):
    new_blocks = []
    for block in data:
        new_block = {"date": block["date"], "total": 0}
        for product in items:
            new_block[product] = block.get(product, 0)
            new_block["total"] += new_block[product]
        new_blocks.append(new_block)
    return new_blocks


def get_year_args():
    duration = get_arg("duration", default="all", choices=("1y", "3y", "5y", "10y", "all"))
    if duration == "all":
        min_year = MIN_DATE.year
    else:
        min_year = MAX_DATE.year - int(duration[:-1])
    return min_year, MAX_DATE.year


def get_date_args():
    """Have an argument called 'duration' that is a string of the form '1d', '4d', '1w', '1m', '3m', '6m', '1y',
    '3y', '5y', '10y', 'all' (default). Turn that into min_date and max_date variables."""
    duration = get_arg("duration", default="all",
                       choices=("1d", "4d", "1w", "1m", "3m", "6m", "1y", "3y", "5y", "10y", "all"))
    time_deltas = {
        "1d": timedelta(days=1),
        "4d": timedelta(days=4),
        "1w": timedelta(weeks=1),
        "1m": timedelta(weeks=4),
        "3m": timedelta(weeks=12),
        "6m": timedelta(weeks=26),
        "1y": timedelta(weeks=52),
        "3y": timedelta(weeks=52 * 3),
        "5y": timedelta(weeks=52 * 5),
        "10y": timedelta(weeks=52 * 10),
    }
    if duration == "all":
        min_date = MIN_DATE
    else:
        min_date = MAX_DATE - time_deltas[duration]
    return min_date, MAX_DATE


def get_top_data_args():
    page = get_arg("page", default=1, coerce_type=int) - 1
    page_size = get_arg("page_size", default=10, coerce_type=int)
    if page < 0:
        page = 0
    if page_size > 500:
        page_size = 500
    if page_size < 1:
        page_size = 1
    return page, page_size


def get_arg(arg_name, default=None, coerce_type=None, choices=()):
    if arg_name in flask.request.args:
        try:
            if coerce_type is datetime:
                value = datetime.strptime(flask.request.args.get(arg_name), "%Y-%m-%d")
            else:
                value = flask.request.args.get(arg_name, type=coerce_type)
        except (TypeError, ValueError):
            return default
        if choices and value not in choices:
            return default
        return value
    return default
