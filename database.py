from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# models

class User(db.Model):

    __tablename__ = 'User'
    
    UserID = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(20), unique=True)
    PwdHash = db.Column(db.String(77))
    AuthToken = db.Column(db.String(64))

class post(db.Model):

    __tablename__ = 'Post'

    postID = db.Column(db.Integer, primary_key=True)
    posterUserName = db.Column(db.String(20))
    imageLink = db.Column(db.String)
    caption = db.Column(db.String)
    verified = db.Column(db.Boolean)


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
