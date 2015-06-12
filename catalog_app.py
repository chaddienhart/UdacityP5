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

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
db_session = DBSession()


@app.route('/')
@app.route('/catalog/')
@app.route('/catalog/<int:user_id>/')
###  the default case of -1 is to represent no user logged in
def catalog(user_id=-1):
    categories = db_session.query(Category).group_by(Category.name).distinct()
    user = ''
    if(user_id > 0):
        user = db_session.query(User).filter_by(id = user_id).one()
    itemgroup = db_session.query(Item).order_by(Item.id).limit(5)
    for i in itemgroup:
        print i.name
    return render_template('catalog.html', categories=categories, items=itemgroup, user=user)


@app.route('/catalog/category/<int:category_id>/')
@app.route('/catalog/category/<int:category_id>/<int:user_id>/')
def viewCategory(category_id, user_id=-1):
    category = db_session.query(Category).filter(Category.id == category_id).first()
    itemgroup = db_session.query(Item).filter(Item.category_id == category_id).all()
    for i in itemgroup:
        print i.name
    user = ''
    if(user_id > 0):
        user = db_session.query(User).filter_by(id = user_id).one()

    return render_template('category.html', category=category, items=itemgroup, user=user)


@app.route('/catalog/addNewItem/<int:user_id>/', methods=['GET', 'POST'])
def newItem(user_id):
    user = db_session.query(User).filter_by(id = user_id).one()
    if request.method == 'POST':
        category_name = request.form['category']
        category = db_session.query(Category).filter_by(name=category_name).one()
        newItem = Item(name=request.form['name'], description=request.form['description'], categories=category, users=user)
        db_session.add(newItem)
        db_session.commit()
        flash(newItem.id) #flash the id so that we can look up the item and tag it as new
        return redirect(url_for('viewCategory', category_id=category.id, user_id=user_id))
    else:
        categories = db_session.query(Category).group_by(Category.name).distinct()
        return render_template('newItem.html', user_id=user_id, categories=categories)


@app.route('/catalog/deleteItem/<int:user_id>/<int:item_id>/<string:item_name>/', methods=['GET', 'POST'])
def deleteItem(user_id, item_id, item_name):
    if request.method == 'POST':
        if request.form['button'] == 'Yes':
            item = db_session.query(Item).filter(Item.id == item_id).one()
            itemCategory = db_session.query(Category).filter(Category.id == item.category_id).one()
            db_session.delete(item)
            db_session.commit()
            return redirect(url_for('viewCategory', category_id=itemCategory.id, user_id=user_id))
        else:
            # button No was pressed, return to the original item
            return redirect(url_for('viewItem', user_id=user_id, item_id=item_id))
    else:
        print item_name
        return render_template('deleteItem.html', user_id=user_id, item_id=item_id, item_name=item_name)


@app.route('/catalog/editItem/<int:user_id>/<int:item_id>/', methods=['GET', 'POST'])
def editItem(user_id, item_id):
    if request.method == 'POST':
        if request.form['button'] == 'Update':
            updated_item = db_session.query(Item).filter_by(id=item_id).one()
            print updated_item.name
            updated_item.name = request.form['name']
            print updated_item.name
            updated_item.description = request.form['description']
            updated_item.picture = request.form['imageUrl']
            print 'post commit'
            db_session.commit()
        return redirect(url_for('viewItem', user_id=user_id, item_id=item_id))
    else:
        item = db_session.query(Item).filter(Item.id == item_id).one()
        print item.name
        item_category = db_session.query(Category).filter_by(id=item.category_id).one()
        print item_category
        return render_template('editItem.html', user_id=user_id, item=item, item_category_name=item_category.name)


@app.route('/catalog/viewItem/<int:user_id>/<int:item_id>/')
def viewItem(user_id, item_id):
    print user_id
    print item_id
    item = db_session.query(Item).filter(Item.id == item_id).one()
    print item.name
    return render_template('item.html', user_id=user_id, item=item)


@app.route('/login/', methods=['GET', 'POST'])
@app.route('/catalog/login/', methods=['GET', 'POST'])
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', state=state)

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

    user_id = getUser(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

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
        # clear the login session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        return redirect(url_for('category'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


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
        return user.id
    except:
        return None


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
