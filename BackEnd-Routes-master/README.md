# InfoSec Backend


## Setup

1. Make sure you have Python 3.8 installed.
2. Install the dependencies with `pip install -r requirements.txt`.
3. Set the environment variable `MONGO_URI` to the URI of the mongo instance. Ask team members for the URI if you don't have it. NEVER push the URI to the repository.
4. If you are running the server in a production environment, set the environment variable `APP_SETTINGS=config.Config`.


## Running

Run the server with `python manage.py runserver`.
