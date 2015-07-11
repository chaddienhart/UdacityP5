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

# import cloudinary
# import cloudinary.uploader
# import cloudinary.api
#
# cloudinary.config(
#   cloud_name = "hi",
#   api_key = "274286359535494",
#   api_secret = "ILYp3Gy3VgjvlrLV8z55CZ-Rt10"
# )


CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
db_session = DBSession()


@app.route('/')
@app.route('/catalog/')
###  the default case of -1 is to represent no user logged in
def catalog():
    categories = db_session.query(Category).group_by(Category.name).distinct()
    user = getCurrentUser()
    itemgroup = db_session.query(Item).order_by(Item.id.desc()).limit(10)
    for i in itemgroup:
        print i.name
    return render_template('catalog.html', categories=categories, items=itemgroup, user=user)


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


@app.route('/catalog/category/<int:category_id>/')
def viewCategory(category_id):
    category = db_session.query(Category).filter(Category.id == category_id).first()
    itemgroup = db_session.query(Item).filter(Item.category_id == category_id).all()
    for i in itemgroup:
        print i.name
    user = getCurrentUser()
    return render_template('category.html', category=category, items=itemgroup, user=user)


@app.route('/catalog/category/<int:category_id>/JSON')
def categoryJSON(category_id):
    category = db_session.query(Category).filter(Category.id == category_id).first()
    itemgroup = db_session.query(Item).filter(Item.category_id == category_id).all()
    for i in itemgroup:
        print i.name
    return jsonify(Category=[item.serialize for item in itemgroup])


@app.route('/catalog/addNewItem/', methods=['GET', 'POST'])
def newItem():
    user = getCurrentUser()
    if request.method == 'POST':
        category_name = request.form['category']
        category = db_session.query(Category).filter_by(name=category_name).one()
        newlocalitem = Item(name=request.form['name'], description=request.form['description'],
                            picture=request.form['imageUrl'], categories=category, users=user)
        db_session.add(newlocalitem)
        db_session.commit()
        flash(newlocalitem.id) #flash the id so that we can look up the item and tag it as new
        return redirect(url_for('viewCategory', category_id=category.id))
    else:
        if user is None:
            return redirect(url_for('login'))
        categories = db_session.query(Category).group_by(Category.name).distinct()
        return render_template('newItem.html', categories=categories, user=user)

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


@app.route('/catalog/editItem/<int:item_id>/', methods=['GET', 'POST'])
def editItem(item_id):
    updated_item = db_session.query(Item).filter_by(id=item_id).one()
    user = getCurrentUser()
    if request.method == 'POST':
        if request.form['button'] == 'Update':
            updated_item.name = request.form['name']
            updated_item.description = request.form['description']
            updated_item.picture = request.form['imageUrl']
            db_session.commit()
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


@app.route('/catalog/myItems/<int:user_id>')
def myItems(user_id):
    user = getCurrentUser()
    # prevent non item owner from viewing myItems
    if user is not None and user_id != user.id:
        # don't give any info if you are not the correct user return to home
        return redirect(url_for('catalog'))
    items = db_session.query(Item).filter_by(user_id = user_id).order_by(Item.category_id).all()
    return render_template('myItems.html', items=items, user=user)


@app.route('/catalog/about/')
def about():
    user = getCurrentUser()
    return render_template('about.html', user=user)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    next = get_redirect_target()
    if next is None:
        next = url_for('catalog')

    #print 'redirect back:'
    #print next
    if request.method == 'POST':
        # login code here
        return redirect_back('login')
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', state=state, next=next)

@app.route('/logout/')
def logout():
    if login_session['provider'] == 'google':
        return redirect(url_for('gdisconnect'))
    if login_session['provider'] == 'facebook':
        return redirect(url_for('fbdisconnect'))
    if login_session['provider'] == 'github':
        return redirect(url_for('ghubdisconnect'))

'''
get authentication from google oauth2
    success: render loginsuccess.html with username and image
        -note: redirects to catalog if successful after 4 seconds see login.html signInCallback signInCallback(authResult)
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
    if result['issued_to'] != CLIENT_ID:
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

    if result['status'] == '200':
        print 'diconnecting'
        # clear the login session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        return redirect(url_for('catalog'))
    else:
        print 'failed to gdisconnect'
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

'''
get authentication from google oauth2
    success: render loginsuccess.html with username and image
        -note: redirects to catalog if successful after 4 seconds see login.html signInCallback signInCallback(authResult)
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
@app.route('/fbconnect/', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = request.data
    app_id = json.loads(open('fbclient_secret.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fbclient_secret.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    http = httplib2.Http()
    result = (http.request(url, 'GET')[1])

    #print "url sent for API access:%s"% url
    #print "API JSON result: %s" % result

    # Use token to get user info from API
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.3/me?%s' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    #print "url sent for API access:%s"% url
    #print "API JSON result: %s" % result

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

    # print login_session['provider']
    # print login_session['username']
    # print login_session['email']
    # print login_session['facebook_id']
    # print login_session['access_token']

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

@app.route('/ghubconnect/', methods=['GET'])
def ghubconnect():
    code = request.args.get('code')
    state = request.args.get('state')
    if state != login_session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    app_id = json.loads(open('ghubclient_secret.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('ghubclient_secret.json', 'r').read())['web']['app_secret']
    # generate a new state just because...
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state

    # make a post request to get a token for the code
    args = (app_id, app_secret, code, state)
    url = ('https://github.com/login/oauth/access_token?client_id={0}&client_secret={1}&code={2}&state={3}'.format(*args))
    http = httplib2.Http()
    result = http.request(url, 'POST')[1]
    resultlist = result.split('&')
    #print resultlist
    login_session['access_token'] = resultlist[0].split('=')[1]
    #print login_session['access_token']

    # get the user name
    url = ('https://api.github.com/user?access_token=%s' % login_session['access_token'])
    result = json.loads(http.request(url, 'GET')[1])
    login_session['username'] = result.get('login')
    login_session['provider'] = 'github'
    login_session['picture'] = result.get('avatar_url')
    print login_session['picture']

    # get the email address
    url = ('https://api.github.com/user/emails?access_token=%s' % login_session['access_token'])
    data = json.loads(http.request(url, 'GET')[1][1:-1]) # there are some extra braces on the returned string, splice off
    login_session['email'] = data.get('email')

    user = getUser(login_session['email'])
    if user is None:
        user = createUser(login_session)
    login_session['user_id'] = user.id

    return redirect(url_for('catalog'))


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


''' see http://flask.pocoo.org/snippets/62/ for redirect snippet reference'''
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
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
