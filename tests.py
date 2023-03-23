# python -m unittest -v tests.py

import unittest, flask_unittest, os, pickle

from flask import Flask
from creds import *
from database import *
from cookie import *

class TestingFlask(flask_unittest.AppTestCase):

    ### test app

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

    ### database tests

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

    def test_add_post(self, app):

        with app.app_context():
            UserID = 3637
            UserName = "test_username"
            Caption = "test caption"

            addPost(UserID, UserName, Caption)
            post = Post.query.filter_by(UserName=UserName).first()

            self.assertEqual(post.UserID, UserID)
            self.assertEqual(post.UserName, UserName)
            self.assertEqual(post.Caption, Caption)

    def test_delete_post(self, app):

        with app.app_context():
            UserID = 38736487
            UserName = "test_username"
            Caption = "test caption"

            addPost(UserID, UserName, Caption)
            post = Post.query.filter_by(UserName=UserName).first()
            
            testPostID = post.PostID
            
            deletePost(testPostID)
            post = Post.query.filter_by(UserName=UserName).first()

            self.assertEqual(post, None)

    def test_toggle_like_post(self, app):

        with app.app_context():
            
            UserID = "87346587"
            UserName = "test_username"
            Caption = "test caption"
            PwdHash = "some hash"

            insertUser(UserName, PwdHash)
            user = User.query.filter_by(UserName=UserName).first()

            addPost(user.UserID, user.UserName, Caption)
            post = Post.query.filter_by(UserName=UserName).first()

            toggleLikePost(UserID, post.PostID)

            self.assertEqual(post.Points, 1)
            self.assertEqual(user.Score, 1)

    def test_toggle_dislike_post(self, app):

        with app.app_context():
            
            UserID = "87346587"
            UserName = "test_username"
            Caption = "test caption"
            PwdHash = "some hash"

            insertUser(UserName, PwdHash)
            user = User.query.filter_by(UserName=UserName).first()

            addPost(user.UserID, user.UserName, Caption)
            post = Post.query.filter_by(UserName=UserName).first()

            toggleDislikePost(UserID, post.PostID)

            self.assertEqual(post.Points, -1)
            self.assertEqual(user.Score, -1)

    def test_add_comment(self, app):

        with app.app_context():
            
            UserName = "test_username"
            Caption = "test caption"
            PwdHash = "some hash"
            Comment = "test comment"

            insertUser(UserName, PwdHash)
            user = User.query.filter_by(UserName=UserName).first()

            addPost(user.UserID, user.UserName, Caption)
            post = Post.query.filter_by(UserName=UserName).first()

            addComment(user.UserID, user.UserName, post.PostID, Comment)

            LDCobj = pickle.loads(post.LDCBlob)

            self.assertTrue((user.UserID, UserName, Comment) in LDCobj.comments)

    ### cookie tests

    def test_make_cookie(self, app):

        with app.app_context():

            UserName = "test_username"
            PwdHash = "some hash"

            insertUser(UserName, PwdHash)
            user = User.query.filter_by(UserName=UserName).first()

            # first make a system cookie
            system_cookie = makeCookie(user, db)

            # now reproduce what it should be
            test_cookie = str(user.UserID) + ':' + user.AuthToken
            mac = hmac.new(COOKIE_SECRET_KEY, test_cookie.encode(), sha256).hexdigest()
            test_cookie = str(user.UserID) + ':' + mac

            self.assertEqual(system_cookie, test_cookie)

    def test_check_for_cookie(self, app):

        with app.app_context():

            username = "test_username"
            passhash = "some hash"

            insertUser(username, passhash)

            user = User.query.filter_by(UserName=username).first()

            # mock request object
            class Request():
                def __init__(self, cookie):
                    self.cookies = { 'rememberme' : cookie }

            usercookie = makeCookie(user, db)
            userrequest = Request(usercookie)

            self.assertTrue(checkForCookie(userrequest, db, User))
    
    def test_get_user_from_cookie(self, app):

        with app.app_context():

            UserName = "test_username"
            PwdHash = "some hash"

            insertUser(UserName, PwdHash)
            user = User.query.filter_by(UserName=UserName).first()

            # mock request object
            class Request():
                def __init__(self, cookie):
                    self.cookies = { 'rememberme' : cookie }

            cookie = makeCookie(user, db)
            request = Request(cookie)

            cookie_user = getUserFromCookie(request, db, User)

            self.assertEqual(user, cookie_user)


if __name__ == '__main__':
    unittest.main()
