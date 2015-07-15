from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json

from flask import make_response
import requests
import os

import cloudinary
import cloudinary.uploader
import cloudinary.api
cloudinary.config(
  cloud_name = "hi",
  api_key = "274286359535494",
  api_secret = "ILYp3Gy3VgjvlrLV8z55CZ-Rt10"
)
cloudinaryurl = "http://res.cloudinary.com/hi/image/upload/"

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
db_session = DBSession()


'''
The 'Home' page for this app
Displays a list of categories on the left and ten most recent items on the right
The current user (or lack of one) determine the if the sign out / sign in button is displayed
if there is a user a welcome message is also displayed in the nav bar
'''
@app.route('/')
@app.route('/catalog/')
def catalog():
    categories = db_session.query(Category).group_by(Category.name).distinct()
    user = getCurrentUser()
    itemgroup = db_session.query(Item).order_by(Item.id.desc()).limit(10)
    return render_template('catalog.html', categories=categories, items=itemgroup, user=user)


'''
Returns tne JSON for the entire catalog, which will contain each category, and within each
category each item.
'''
@app.route('/catalog/JSON')
def catalogJSON():
    categories = db_session.query(Category).all()
    serializedCat = []
    for cat in categories:
        newCat = cat.serialize
        items = db_session.query(Item).filter_by(category_id = cat.id).all()
        serialItems = []
        for i in items:
            serialItems.append(i.serialize)
        newCat['items'] = serialItems
        serializedCat.append(newCat)
    return jsonify(Catalog=[serializedCat])


'''
Displays the category with a link to add a new item.
If the user is not logged in they will be asked to sign in after pressing the Add new item button
after signing in they will then be redirected to the category page again.
'''
@app.route('/catalog/category/<int:category_id>/')
def viewCategory(category_id):
    category = db_session.query(Category).filter(Category.id == category_id).first()
    itemgroup = db_session.query(Item).filter(Item.category_id == category_id).all()
    user = getCurrentUser()
    return render_template('category.html', category=category, items=itemgroup, user=user)


'''
Returns the JSON for the items in the category_id requested.
If the category does not exist, an empty list is returned.
'''
@app.route('/catalog/category/<int:category_id>/JSON')
def categoryJSON(category_id):
    category = db_session.query(Category).filter(Category.id == category_id).first()
    itemgroup = db_session.query(Item).filter(Item.category_id == category_id).all()
    return jsonify(Category=[item.serialize for item in itemgroup])


'''
Adding new items can only be done by authenticated users, redirect to login if not signed in (user == None)
GET brings up the newItem template
POST will either add a new item to the database or clean up any photos that were uploaded and redirect
back to the category
'''
@app.route('/catalog/addNewItem/<int:category_id>/', methods=['GET', 'POST'])
def newItem(category_id):
    user = getCurrentUser()
    if request.method == 'POST':
        if request.form['button'] == 'Create' and request.form['name'] != None and request.form['name'] != '':
            category_name = request.form['category']
            category = db_session.query(Category).filter_by(name=category_name).one()
            category_id = category.id
            newlocalitem = Item(name=request.form['name'], description=request.form['description'],
                                picture=request.form['imageUrl'], categories=category, users=user)
            db_session.add(newlocalitem)
            db_session.commit()
        else:
            # remove the new image if the user uploaded and then chose to not update the item
            if request.form['imageUrl'] != None:
                cloudinary.api.delete_resources([os.path.splitext(os.path.basename(request.form['imageUrl']))[0]])
        return redirect(url_for('viewCategory', category_id=category_id))
    else:
        if user is None:
            return redirect(url_for('login'))
        categories = db_session.query(Category).group_by(Category.name).distinct()
        return render_template('newItem.html', categories=categories, user=user, category_id=category_id)


'''
Deleting an item can only be performed by the owner, if not the user return to the item view
Verify that the user wants to delete the item and protect against CSRF by creating a unique token
when verifying and checking that the token matches on the POST request
'''
@app.route('/catalog/deleteItem/<int:item_id>/', methods=['GET', 'POST'])
def deleteItem(item_id):
    user = getCurrentUser()
    item = db_session.query(Item).filter(Item.id == item_id).one()
    # prevent non item owner from deleting the item, redirect anyone else
    if user is not None and item.user_id != user.id:
        return redirect(url_for('viewItem', item_id=item_id))

    if request.method == 'POST':
        # verify the request came from the user confirming deletion
        if request.args.get('csrf') != login_session['csrf']:
            response = make_response(json.dumps('invalid state parameter'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        if request.form['button'] == 'Yes':
            itemCategory = db_session.query(Category).filter(Category.id == item.category_id).one()
            # remove the image from cloudinary storage
            if item.picture != None:
                cloudinary.api.delete_resources([os.path.splitext(os.path.basename(item.picture))[0]])
            db_session.delete(item)
            db_session.commit()
            return redirect(url_for('viewCategory', category_id=itemCategory.id))
        else:
            # button No was pressed, return to the original item
            return redirect(url_for('viewItem', item_id=item_id))
    else:
        csrf = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
        login_session['csrf'] = csrf
        return render_template('deleteItem.html', item=item, user=user, csrf=csrf)


'''
similar to adding a new item except the button is update instead of create.
'''
@app.route('/catalog/editItem/<int:item_id>/', methods=['GET', 'POST'])
def editItem(item_id):
    updated_item = db_session.query(Item).filter_by(id=item_id).one()
    user = getCurrentUser()
    if request.method == 'POST':
        if request.form['button'] == 'Update' and request.form['name'] != None and request.form['name'] != '':
            updated_item.name = request.form['name']
            updated_item.description = request.form['description']
            # remove the old picture if it is being updated
            if updated_item.picture != request.form['imageUrl'] and updated_item.picture != None:
                cloudinary.api.delete_resources([os.path.splitext(os.path.basename(updated_item.picture))[0]])
            updated_item.picture = request.form['imageUrl']
            db_session.commit()
        else:
            # remove the new image if the user uploaded and then chose to not update the item
            if request.form['imageUrl'] != None:
                cloudinary.api.delete_resources([os.path.splitext(os.path.basename(request.form['imageUrl']))[0]])

        return redirect(url_for('viewItem', item_id=item_id))
    else:
        categories = db_session.query(Category).group_by(Category.name).distinct()
        return render_template('editItem.html', item=updated_item, categories=categories, user=user)


@app.route('/catalog/viewItem/<int:item_id>/')
def viewItem(item_id):
    item = db_session.query(Item).filter(Item.id == item_id).one()
    user = getCurrentUser()
    return render_template('item.html', item=item, user=user)


@app.route('/catalog/viewItem/<int:item_id>/JSON')
def itemJSON(item_id):
    item = db_session.query(Item).filter_by(id = item_id).one()
    return jsonify(Item=item.serialize)

'''
Renders a page with all the items added by the user as long as they are currently signed in
'''
@app.route('/catalog/myItems/<int:user_id>')
def myItems(user_id):
    user = getCurrentUser()
    # prevent non item owner from viewing myItems
    if user is None or user_id != user.id:
        # don't give any info if you are not the correct user return to home
        return redirect(url_for('catalog'))
    items = db_session.query(Item).filter_by(user_id = user_id).order_by(Item.category_id).all()
    return render_template('myItems.html', items=items, user=user)


'''
Returns the JSON for the items added by the user_id requested, only if that is the current user
If the user is not the current user return an empty list is returned.
'''
@app.route('/catalog/myItems/<int:user_id>/JSON')
def myItemsJSON(user_id):
    user = getCurrentUser()
    # prevent non item owner from viewing myItems
    if user is None or user_id != user.id:
        # return empty
        return jsonify(Category=[None])
    items = db_session.query(Item).filter_by(user_id = user_id).order_by(Item.category_id).all()
    return jsonify(Category=[item.serialize for item in items])


'''
Provide some background info on the app, user is needed for use in the bootstrap nav bar
'''
@app.route('/catalog/about/')
def about():
    user = getCurrentUser()
    return render_template('about.html', user=user)


'''
displays the login page with a list of supported OAuth2 providers for authentication
get the redirect target so that the request returns to the page that the request to originate came from
'''
@app.route('/login/', methods=['GET', 'POST'])
def login():
    next = get_redirect_target()
    if next is None:
        next = url_for('catalog')

    if request.method == 'POST':
        return redirect_back('login')
    # guard against forgery attacks by creating a state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', state=state, next=next)


'''
Create a single html location to call to logout, call the correct disconnect from here based on the
current authentication provider.
'''
@app.route('/logout/')
def logout():
    if login_session['provider'] == 'google':
        return redirect(url_for('gdisconnect'))
    if login_session['provider'] == 'facebook':
        return redirect(url_for('fbdisconnect'))
    if login_session['provider'] == 'github':
        return redirect(url_for('ghubdisconnect'))

'''
get authentication from Google oauth2
    success: render loginsuccess.html with username and image
        -note: redirects to catalog if successful after 4 seconds see signin.html signInCallback
    failure: return error code and remain on login screen
    1. verify the login_session['state'] matches to guard against cross site impersonation
    2. use oauth2client.client to get credentials from the code (passed in as request.data)
    3. use the token to get info, send and error if the token is invalid
    4. verify the token is for the credentialed user
    5. verify the token was intended to for use by this app
    6. check to see it the current user is already logged in if so return with 200
    7. create a new user if needed, store the users info in the login_session
    8. redirect (temporarily) to loginsuccess.html (see note above)
'''
GOOGLEID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']
@app.route('/gconnect/', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(request.data)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    http = httplib2.Http()
    result = json.loads(http.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != GOOGLEID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # check to see if this user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    data = requests.get(userinfo_url, params=params).json()

    # Store the access token and other user info in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user = getUser(login_session['email'])
    if user is None:
        user = createUser(login_session)
    login_session['user_id'] = user.id

    flash("Logged in as %s" % login_session['username'])
    return render_template('loginsuccess.html', username=login_session['username'], picture=login_session['picture'])


'''
    disconnect login by revoking current login_session token
    delete login_session data
'''
@app.route("/gdisconnect/")
def gdisconnect():
    access_token = login_session['access_token']
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    http = httplib2.Http()
    result = http.request(url, 'GET')[0]

    if result['status'] != '200':
        print 'failed to gdisconnect'
        # # For whatever reason, the given token was invalid. We still want to log out the current user

    # clear the login session
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    return redirect(url_for('catalog'))


'''
get authentication from Facebook oauth2
    success: render loginsuccess.html with username and image
        -note: redirects to catalog if successful after 4 seconds see signin.html sendTokenToServer
    failure: return error code and remain on login screen
    1. verify the login_session['state'] matches to guard against cross site impersonation
    2. request a token
    3. use the token to get info, send and error if the token is invalid
    4. create a new user if needed, store the users info in the login_session
    5. redirect (temporarily) to loginsuccess.html (see note above)
'''
FBID = json.loads(open('fbclient_secret.json', 'r').read())['web']['app_id']
FBSCRT = json.loads(open('fbclient_secret.json', 'r').read())['web']['app_secret']
@app.route('/fbconnect/', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = request.data
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        FBID, FBSCRT, access_token)
    http = httplib2.Http()
    result = (http.request(url, 'GET')[1])

    # Use token to get user info from API
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.3/me?%s' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # If there was an error in the access token info, abort.
    if 'error' in result:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.2/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    user = getUser(login_session['email'])
    if user is None:
        user = createUser(login_session)
    login_session['user_id'] = user.id

    flash("Logged in as %s" % login_session['username'])
    return render_template('loginsuccess.html', username=login_session['username'], picture=login_session['picture'])


'''
    disconnect login by revoking current login_session token
    delete login_session data
'''
@app.route('/fbdisconnect/')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    print facebook_id
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    print access_token
    url = 'https://graph.facebook.com/%s/permissions' % access_token
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    print 'diconnecting result:'
    print result

    # clear the login session
    del login_session['access_token']
    del login_session['facebook_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['provider']
    del login_session['user_id']
    return redirect(url_for('catalog'))


'''
Get Authentication from GitHub OAuth2
    success: render catalog.html with username and image
    failure: return error code and remain on login screen
    1. verify the login_session['state'] matches to guard against cross site impersonation
    2. use the code returned from authorization request to request an access token
    3. use the token to get info, send and error if the token is invalid
    4. create a new user if needed, store the users info in the login_session
    5. redirect to catalog.html
'''
GHID = json.loads(open('ghubclient_secret.json', 'r').read())['web']['app_id']
GHSCRT = json.loads(open('ghubclient_secret.json', 'r').read())['web']['app_secret']
@app.route('/ghubconnect/', methods=['GET'])
def ghubconnect():
    code = request.args.get('code')
    state = request.args.get('state')
    if state != login_session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # generate a new state because the old one was sent in the link params
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state

    # make a post request to get a token for the code
    args = (GHID, GHSCRT, code, state)
    url = ('https://github.com/login/oauth/access_token?client_id={0}&client_secret={1}&code={2}&state={3}'.format(*args))
    http = httplib2.Http()
    result = http.request(url, 'POST')[1]
    resultlist = result.split('&')
    login_session['access_token'] = resultlist[0].split('=')[1]

    # get the user name
    url = ('https://api.github.com/user?access_token=%s' % login_session['access_token'])
    result = json.loads(http.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if 'error' in result:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['username'] = result.get('login')
    login_session['provider'] = 'github'
    login_session['picture'] = result.get('avatar_url')

    # get the email address
    url = ('https://api.github.com/user/emails?access_token=%s' % login_session['access_token'])
    data = json.loads(http.request(url, 'GET')[1][1:-1]) # there are some extra braces on the returned string, splice off
    login_session['email'] = data.get('email')

    user = getUser(login_session['email'])
    if user is None:
        user = createUser(login_session)
    login_session['user_id'] = user.id

    return redirect(url_for('catalog'))


'''
    disconnect login by deleting the login_session data
    users can revoke access from their GitHub account, under Personal settings/Applications
'''
@app.route('/ghubdisconnect/')
def ghubdisconnect():
    # clear the login session
    del login_session['access_token']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['provider']
    del login_session['user_id']
    return redirect(url_for('catalog'))


''' Helper functions '''
def createUser(login_session):
    # create the user object, add it to the db, and commit the change
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    db_session.add(newUser)
    db_session.commit()
    # get the new user id from the database
    return getUser(login_session['email'])


def getUserInfo(user_id):
    user = db_session.query(User).filter_by(id = user_id).one()
    return user


def getUser(email):
    try:
        user = db_session.query(User).filter_by(email = email).one()
        return user
    except:
        return None

def getCurrentUser():
    user = None
    if 'email' in login_session:
        user = getUser(login_session['email'])
    else:
        print 'user logged out'
        print user
    return user


'''
some code to get request orign to redirect back after going to the login page
see http://flask.pocoo.org/snippets/62/ for redirect snippet reference
'''
def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        return target


def redirect_back(endpoint, **values):
    print endpoint
    print values
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)
''' end redirect snippet reference'''


if __name__ == "__main__":
    app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
