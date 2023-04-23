from flask import Blueprint, render_template, redirect, url_for, request, make_response, flash
from passlib.hash import argon2
from database import *
from cookie import *
from creds import *

core = Blueprint('core', __name__, template_folder='templates')

@core.route("/")

def index():
    return render_template('index.html')

@core.route("/about")

def about():
    return render_template('about.html')

@core.route("/login", methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        # load form data
        username, password = request.form['username'], request.form['password']

        # Check if all the fields are filled out
        if not any((username, password)):
            return render_template('login.html', error="All fields are required")

        # check the database to see if the user exists
        search = User.query.filter_by(UserName=username).first()
        if search is None: 
            return render_template('login.html', error="User not found")

        # check the password
        if not argon2.verify(password, search.PwdHash):
            return render_template('login.html', error="Incorrect password")

        # set authentication cookie
        resp = make_response(redirect(url_for('core.main')))
        cookie = makeCookie(search, db)
        resp.set_cookie('rememberme', cookie)
        return resp
    
    if request.method == 'GET':
        if checkForCookie(request, db, User):
            return redirect(url_for('core.main'))
        else:
            return render_template('login.html')

@core.route('/main', methods=['GET','POST'])

def main():
    # user isn't authorised
    if not checkForCookie(request, db, User):
        return redirect(url_for('core.login'))

    user = getUserFromCookie(request, db, User)
    
    # new post, like, dislike or comment
    if request.method == "POST":

        if request.form["engagement"] == 'LIKE':
            postid = request.form['postid']
            toggleLikePost(user.UserID, postid)

        elif request.form["engagement"] == 'DISLIKE':
            postid = request.form['postid']
            toggleDislikePost(user.UserID, postid)

        elif request.form["engagement"] == 'COMMENT':
            postid, comment = request.form['postid'], request.form['comment']
            if comment:
                addComment(user.UserID, user.UserName, postid, comment)

        elif request.form["engagement"] == 'POST':
            caption, image = request.form['caption'], request.form['image']
            addPost(user.UserID, user.UserName, caption, image)

    # get display information
    posts = (getHighestRankedPosts if EVALUATION_MODE else getMostRecentPosts)()
    comments = getCommentListFromPosts(posts)
    likestatuss = getLikeStatussFromPosts(posts, user.UserID)
    userpoints = getUserPointsFromPosts(posts)

    # send the user data with the response
    return render_template(
        'main.html', 
        user=user, 
        posts=posts, 
        comments=comments,
        likestatuss=likestatuss,
        userpoints=userpoints
    )

@core.route('/logout')

def logout():
    resp = make_response(redirect(url_for('core.index')))

    if 'rememberme' in request.cookies:
        # get the cookie
        remember_cookie = request.cookies.get("rememberme")
        
        # Search for the users id
        user_id = remember_cookie.split(":")[0]
        search = User.query.filter_by(UserID=user_id).first()

        # Delete the random authenitcation token in the db
        search.AuthToken = ""
        db.session.commit()

        # Delete the cookie
        resp.set_cookie('rememberme', '', expires=0)

    return resp

@core.route('/signup', methods=['GET', 'POST'])

def signup():
    if request.method == 'POST':
        form = request.form
        errors = []

        # check passwords match
        if form["password"] != form["retypepassword"]:
            errors.append("Passwords don't match")

        # check username availability
        check = User.query.filter_by(UserName=form["username"]).first()
        if check is not None:
            errors.append("Username is already taken")

        # check all fields have been filled in
        if (form['username'] == "" or 
            form['password'] == "" or 
            form["retypepassword"] == ""):
            errors.append("All fields are required")

        # check username is short enough
        if len(form['username']) > 20:
            errors.append("Max username length is 20 characters")

        # check password is long enough
        if len(form['password']) < 8:
            errors.append("Password is too short")

        # add new user to database
        if errors == []:
            insertUser(form['username'], argon2.hash(form['password']))
            return redirect(url_for("core.login"))

        flash(errors)
        return render_template('signup.html')
    
    if request.method == 'GET':
        return render_template('signup.html')
