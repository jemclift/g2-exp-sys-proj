from flask import Flask
from creds import *
from database import *

app = Flask(__name__)
app.secret_key = FLASH_SECRET_KEY

# database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# run to generate database
# with app.app_context(): db.create_all()

# routes

from views import core
app.register_blueprint(core)

if __name__ == "__main__":
    app.run()