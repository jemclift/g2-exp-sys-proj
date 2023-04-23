from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
import pickle
from creds import *

db = SQLAlchemy()

# database models

class User(db.Model):

    __tablename__ = 'User'
    
    UserID = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(20), unique=True)
    PwdHash = db.Column(db.String(77))
    AuthToken = db.Column(db.String(64))
    Score = db.Column(db.Integer)

    # D4 Evaluation
    Interactions = db.Column(db.Integer)

class Post(db.Model):

    __tablename__ = 'Post'

    PostID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer)
    UserName = db.Column(db.String(20))
    Caption = db.Column(db.String)
    Verified = db.Column(db.Boolean)

    # likes - dislikes
    Points = db.Column(db.Integer)

    # UTC datetime
    Date = db.Column(db.DateTime)

    # links to the image on the server
    ImageLink = db.Column(db.String)

    # python pickle blob to store likes, dislikes and comments
    LDCBlob = db.Column(db.PickleType)

# like dislike and comment class

class LDC:
    def __init__(self):
        # stores comments as a list of tuples of form (userid, comment)
        self.comments = []
        # stores likes and dislikes as sets of userids which have liked/disliked the post
        self.likes = set()
        self.dislikes = set()

    def __repr__(self):
        output = ["\n(L)ike, (D)islike & (C)omment Object\n"]
        for comment in self.comments:
            output.append(f"[COMMENT] user {comment[0]}: '{comment[1]}'")
        output.append(f"[LIKES] {str(self.likes)}")
        output.append(f"[DISLIKES] {str(self.dislikes)}")
        return "\n".join(output)

    def addComment(self, userid, username, comment):
        self.comments.append((userid, username, comment))
    
    def toggleLike(self, userid):
        # user hasn't liked or disliked post yet
        if userid not in self.likes | self.dislikes: 
            self.likes.add(userid)
            return 1
        
        # user has liked the post
        elif userid in self.likes:
            self.likes.remove(userid)
            return -1

        # user has disliked the post
        elif userid in self.dislikes:
            self.dislikes.remove(userid)
            self.likes.add(userid)
            return 2

    def toggleDislike(self, userid):
        # user hasn't liked or disliked post yet
        if userid not in self.likes | self.dislikes:
            self.dislikes.add(userid)
            return -1

        # user has liked the post
        elif userid in self.likes:
            self.likes.remove(userid)
            self.dislikes.add(userid)
            return -2

        # user has disliked the post
        elif userid in self.dislikes:
            self.dislikes.remove(userid)
            return 1

# create post

def addPost(userid, username, caption, imagelink=""):

    new_post = Post(
        UserID=userid, 
        UserName=username,
        Caption=caption,
        Verified=False,
        Points=0,
        Date=datetime.now(),
        ImageLink="" if imagelink == "" else imagelink,
        LDCBlob = pickle.dumps(LDC()) # empty LDC object
    )

    db.session.add(new_post)
    db.session.commit()

# delete post

def deletePost(postid):

    post = Post.query.filter_by(PostID=postid).first()

    if post is not None:
        db.session.delete(post)
        db.session.commit()

# post interactions

def toggleLikePost(userid, postid):

    post = Post.query.filter_by(PostID=postid).first()

    # find the poster
    user = User.query.filter_by(UserID=post.UserID).first()
    
    LDCobj = pickle.loads(post.LDCBlob)
    user.Score += LDCobj.toggleLike(userid)
    post.Points = len(LDCobj.likes) - len(LDCobj.dislikes)
    # print("points",post.Points)
    post.LDCBlob = pickle.dumps(LDCobj)

    db.session.commit()

def toggleDislikePost(userid, postid):

    post = Post.query.filter_by(PostID=postid).first()

    # find the poster
    user = User.query.filter_by(UserID=post.UserID).first()
    
    LDCobj = pickle.loads(post.LDCBlob)
    user.Score += LDCobj.toggleDislike(userid)
    post.Points = len(LDCobj.likes) - len(LDCobj.dislikes)
    # print("points",post.Points)
    post.LDCBlob = pickle.dumps(LDCobj)

    db.session.commit()

def addComment(userid, username, postid, comment):
    # find the user and post
    user = User.query.filter_by(UserID=userid).first()
    post = Post.query.filter_by(PostID=postid).first()

    # un-pickle the blob, add comment, re-pickle
    LDCobj = pickle.loads(post.LDCBlob)
    LDCobj.addComment(userid, username, comment)
    post.LDCBlob = pickle.dumps(LDCobj)

    db.session.commit()

# returns a lists of comment dictionarys for some list of posts

def getCommentListFromPosts(posts):
    comments = []

    for post in posts:
        LDCobj = pickle.loads(post.LDCBlob)
        comments.append(LDCobj.comments)
    
    return comments

# given a list of posts and a userid, returns a list of -1,0,1 for each interaction

def getLikeStatussFromPosts(posts, userid):
    like_statuss = []

    for post in posts:
        LDCobj = pickle.loads(post.LDCBlob)

        if userid in LDCobj.likes:      like_statuss.append(1)
        elif userid in LDCobj.dislikes: like_statuss.append(-1)
        else:                           like_statuss.append(0)

    return like_statuss

# returns a list of the poster's points for a list of posts

def getUserPointsFromPosts(posts):
    user_points = []
    # cache users points to dictionary
    users = {}

    for post in posts:
        userid = post.UserID

        # cache miss
        if userid not in users:
            user = User.query.filter_by(UserID=userid).first()
            users[userid] = user.Score

        user_points.append(users[userid])

    return user_points

# get n most recent posts

def getMostRecentPosts(n=100):

    posts = Post.query.order_by(desc(Post.Date)).limit(n).all()
    return posts

# get n highest ranked posts

def getHighestRankedPosts(n=100):

    def calculatePostRanking(post):

        rank = post.Points

        if post.Verified:
            rank += VERIFIED_POST_RANKING_BOOST

        return rank

    posts = getMostRecentPosts(n)

    return sorted(posts, key=calculatePostRanking, reverse=True)

# insert a user with the given name and password hash. 

def insertUser(UserName, PwdHash):

    # return false if the username already exists
    user = User.query.filter_by(UserName=UserName).first()
    if user is not None: return False

    # add the new user
    new = User(UserName=UserName, PwdHash=PwdHash, Score=0, Interactions=0)
    db.session.add(new)
    db.session.commit()

# deletes a user with the given name (if they exist)

def deleteUser(UserName):

    # search for the username
    user = User.query.filter_by(UserName=UserName).first()

    # delete it if it exists
    if user is not None:
        db.session.delete(user)
        db.session.commit()
