import secrets, hmac
from hashlib import sha256
from creds import *

# makes an auth cookie for succesful login

def makeCookie(search, db):

    # assign a new random token to the user in the db
    token = secrets.token_hex()
    search.AuthToken = token
    db.session.commit()

    # add the id and the token to the cookie string
    cookie = str(search.UserID) + ':' + token

    # hash the cookie string
    mac = hmac.new(COOKIE_SECRET_KEY, cookie.encode(), sha256).hexdigest()
    cookie = str(search.UserID) + ':' + mac

    return cookie

# checks if the user holds a valid cookie

def checkForCookie(request, db, User):

    if 'rememberme' in request.cookies:

        # generate what a valid cookie for this user would look like
        remember_cookie = request.cookies.get("rememberme")
        user_id = remember_cookie.split(":")[0]

        search = User.query.filter_by(UserID=user_id).first()
        if not search: return False

        rnd_auth_token = search.AuthToken
        if not rnd_auth_token: return False

        cookie = user_id + ':' + rnd_auth_token
        mac = hmac.new(COOKIE_SECRET_KEY, cookie.encode(), sha256).hexdigest()
        cookie = user_id + ':' + mac

        # compare the theoretical cookie to the actual cookie
        return remember_cookie == cookie

# returns the database record for valid cookie

def getUserFromCookie(request, db, User):

    if 'rememberme' in request.cookies:

        remember_cookie = request.cookies.get("rememberme")
        user_id = remember_cookie.split(":")[0]

        return User.query.filter_by(UserID=user_id).first()

# D4 Evaluation

def userInteraction(request, db, User):

    if checkForCookie(request, db, User):
        user = getUserFromCookie(request, db, User)
        user.Interactions += 1
        print(f"USER {user.UserName} incremented to {user.Interactions}")
        db.session.commit()
