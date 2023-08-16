from flask_script import Manager
from flask_cors import CORS
import os
from web import app

CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_ALLOW_HEADERS'] = ['Content-Type', 'Authorization']
app.config['CORS_ALLOW_METHODS'] = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
manager = Manager(app)
#app.debug = True



if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    manager.run()