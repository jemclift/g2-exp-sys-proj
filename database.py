from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime

db = SQLAlchemy()

# models

class User(db.Model):

    __tablename__ = 'User'
    
    UserID = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(20), unique=True)
    PwdHash = db.Column(db.String(77))
    AuthToken = db.Column(db.String(64))

class Post(db.Model):

    __tablename__ = 'Post'

    postID = db.Column(db.Integer, primary_key=True)
    posterUserName = db.Column(db.String(20))
    imageLink = db.Column(db.String)
    caption = db.Column(db.String)
    verified = db.Column(db.Boolean)

    # UTC datetime
    Date = db.Column(db.DateTime)

    # links to the image on the server and the json database
    ImageLink = db.Column(db.String)
    PointsLink = db.Column(db.String)

# create post

def addPost(userid, caption, imagelink=""):

    new_post = Post(
        UserID=userid, 
        Caption=caption,
        Verified=False,
        Points=0,
        Date=datetime.now(),
        ImageLink="" if imagelink == "" else imagelink,
        PointsLink=""
    )

    db.session.add(new_post)
    db.session.commit()

# delete post

def deletePost(postid):

    post = Post.query.filter_by(PostID=postid).first()

    if post is not None:
        post.delete()
        db.session.commit()

# get n most recent posts

def getMostRecentPosts(n=10):

    posts = Post.query.order_by(desc(Post.Date)).limit(n).all()
    return posts

# insert a user with the given name and password hash. 

def insertUser(UserName, PwdHash):

    # return false if the username already exists
    user = User.query.filter_by(UserName=UserName).first()
    if user is not None: return false

    # add the new user
    new = User(UserName=UserName, PwdHash=PwdHash)
    db.session.add(new)
    db.session.commit()

# deletes a user with the given name (if they exist)

def deleteUser(UserName):

    # search for the username
    user = User.query.filter_by(UserName=UserName).first()

    # delete it if it exists
    if user is not None:
        user.delete()
        db.session.commit()
