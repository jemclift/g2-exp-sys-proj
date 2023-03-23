# python -m unittest -v tests.py

import flask_unittest
import os
import pickle

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

    def test_add_Comment(self, app):

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

    def test_getUserPointsFromPosts (self, app):

        with app.app_context():
            
            UserName =  "test_username"
            PwdHash = "some hash"
            Caption = "test caption"

            insertUser(UserName, PwdHash)  
            user = User.query.filter_by(UserName=UserName).first()

            addPost (user.UserID, UserName, Caption) 
            post = Post.query.filter_by(UserID = user.UserID).first()
            
            toggleLikePost (user.UserID, post.PostID)
            post = Post.query.order_by(desc(Post.Date)).limit(100).all()

            test_posts = getUserPointsFromPosts(post)
            
            self.assertEqual(test_posts[0], 1)