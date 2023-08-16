import os
from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.from_object(os.environ.get("APP_SETTINGS", "config.DevelopmentConfig"))

from web import routes
