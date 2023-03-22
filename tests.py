# python -m unittest -v tests.py

import flask_unittest
import os

from flask import Flask
from creds import *
from database import *

class TestingFlask(flask_unittest.AppTestCase):

    def create_app(self):

        app = Flask(__name__)
        app.secret_key = FLASH_SECRET_KEY

        return app

    def setUp(self, app):

        # remove old db
        path = 'instance/test.sqlite3'
        if os.path.exists(path):
            os.remove(path)

        # new database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite3'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

        # generate database
        with app.app_context(): 
            db.create_all()

        # routes
        from views import core
        app.register_blueprint(core)

    def test_create_user(self, app):

        with app.app_context():
            
            UserName = "test_username"
            PwdHash = "some hash"

            insertUser(UserName, PwdHash)

            user = User.query.filter_by(UserName=UserName).first()

            self.assertEqual(user.UserName, UserName)
            self.assertEqual(user.PwdHash, PwdHash)

    def test_delete_user(self, app):

        with app.app_context():

            UserName = "test_username"
            PwdHash = "some hash"

            insertUser(UserName, PwdHash)
            deleteUser(UserName)

            user = User.query.filter_by(UserName=UserName).first()

            self.assertEqual(user, None)

# if __name__ == '__main__':
    # flask_unittest.main.unittest.main()