from flask import Flask, flash, jsonify, redirect, render_template,\
								request, url_for
from flask import session as login_session
# login_session is a dictionary that stores users login details for the duration of their session

import random, string
import pprint as pp # for pretty-printing
# from collections import OrderedDict # to enable sorting on nested dictionaries

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item
import time

from oauth2client.client import flow_from_clientsecrets
# creates a flow objectfrom clientsecrets JSON file. Stores client Id and other oAuth parameters
from oauth2client.client import FlowExchangeError
# this will catch errors when trying to exchange an authorisation code for an access token.


import httplib2 # comprehensive http clientlibrary in python
import json
from flask import make_response #converts the return value from a function into a real response object to send to client
import requests

GOOGLE_CLIENT_ID = json.loads(
				open('google_client_secret.json','r').read())['web']['client_id']

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/catalog/', methods=['GET'])
def showCatalog():
	categories = session.query(Category).order_by(Category.name)
	# for category in categories:
					# pp.pprint(category.serialize)
	items = session.query(Item).order_by(Item.edited_time).limit(5)
	latest_items = []
	for item in items:
		latest_items.append(item.serialize)
	for item in latest_items:
		item['category_name'] = session.query(Category).filter_by(id = item['category_id']).one().name
	return render_template('catalog.html', categories=categories,
																																																	latest_items = latest_items)

@app.route('/createCategory/', methods = ['GET','POST'])
def createCategory():
	# print (request.form)
	if request.method =='GET':
		return redirect(url_for('showCatalog'))
	elif request.method =='POST':
		category_name = request.form['name']
		if session.query(Category).filter_by(name = category_name).first():
			flash('Category: {} already exits'.format(category_name))
		else:
			newCategory = Category(name=category_name)
			session.add(newCategory)
			session.commit()
			flash('{} created'.format(newCategory.name))
	return redirect(url_for('showCatalog'))

@app.route('/createItem/', methods=['POST'])
def createItem():
	pp.pprint (request.form)
	newItem = Item()
	if request.form['name']:
		newItem.name = request.form['name']
	if request.form['description']:
		newItem.description = request.form['description']
	if request.form['category_id']:
		newItem.category_id = request.form['category_id']
	if request.form['user_id']:
		newItem.user_id = request.form['user_id']
	for key in request.form:
		print(key, ': ', request.form[key] )
	newItem.edited_time = int(time.time())
	session.add(newItem)
	session.commit()
	flash('{} created'.format(newItem.name))
	return jsonify(newItem.serialize)

@app.route('/editCategory/<int:id>', methods = ['POST'])
def editCategory(id):
	if request.method == 'POST':
		print (request.form)
		category_to_edit = session.query(Category).filter_by(id=id).one()
		print ('category to edit retrieved from database')
		pp.pprint(category_to_edit.serialize)
		if request.form['name']:
			category_to_edit.name = request.form['name']
		session.add(category_to_edit)
		session.commit(category_to_edit)
		flash('{} edited'.format(category_to_edit.name))
		return redirect(url_for('showCatalog'))

@app.route('/editItem/<int:id>', methods=['POST'])
# will want to combine this into one route, with GET and POST items maybe?
def editItem(id):
	edited_time = int(time.time())
	if request.method=='POST':
		item_to_edit = session.query(Item).filter_by(id = id).one()
		print ('item to edit retrieved from database')
		pp.pprint (item_to_edit.serialize)
		if request.form['name']:
			item_to_edit.name = request.form['name']
		if request.form['description']:
			item_to_edit.description = request.form['description']
		if request.form['category_id']:
			item_to_edit.category_id = request.form['category_id']
		if request.form['user_id']:
			item_to_edit.user_id = request.form['user_id']
		for key in request.form:
			print(key, ': ', request.form[key] )
		if request.form != []:
			item_to_edit.edited_time = edited_time
		session.add(item_to_edit)
		session.commit()
		parent_category = session.query(Category).filter_by(id = item_to_edit.category_id).first()
		flash('{} edited'.format(item_to_edit.name))
		return redirect(url_for('item_display', category=parent_category.name,
																																																		item = item_to_edit.name))

@app.route('/deleteCategory/<int:id>', methods = ['GET', 'POST'])
def deleteCategory(id):
	category_to_delete = session.query(Category).filter_by(id=id).first()
	# We also need to delete the items associated with the category
	items_to_delete = session.query(Item).filter_by(category_id = id).all()
	if request.method == 'GET':
		return render_template('deleteCategory.html', category = category_to_delete, \
																																														 items = items_to_delete)
	elif request.method == 'POST':
		session.delete(category_to_delete)
		if (items_to_delete):
			for item in items_to_delete:
				session.delete(item)
		session.commit()
		flash('{} deleted'.format(category_to_delete.name))
		return redirect(url_for('showCatalog'))

@app.route('/deleteItem/<int:id>', methods = ['GET', 'POST'])
def deleteItem(id):
	item_to_delete = session.query(Item).filter_by(id = id).first()
	if request.method == 'GET':
		return render_template('deleteItem.html', item = item_to_delete)
	elif request.method == 'POST':
		item_category_id = item_to_delete.category_id
		# print ('item_to_delete.category_id is: {}'.format(item_to_delete.category_id))
		category = session.query(Category).filter_by(id = item_category_id).one()
		# print (category.serialize)
		session.delete(item_to_delete)
		session.commit()
		flash('{} deleted'.format(item_to_delete.name))
		return redirect(url_for('category_display', category = category.name))

@app.route('/login/', methods=['GET'])
def login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
																									for x in range(32))
	login_session['state'] = state
	# print ('state is {}'.format(state))
	return render_template('login.html', STATE=login_session['state'])

@app.route('/gconnect', methods = ['POST'])
def gconnect():
	print ('POST /gconnect received')
	# Validate the state token
	if request.args.get('state') != login_session['state']:
		print ('invalid state parameter')
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# If it passes that, then we next obtain a one-time authorisation code.
	print ("state parameter was valid. Obtaining a one-time authorisation code")
	code = request.data # this will only happen if the if statement above is false - i.e. the state variable matches correctly.
	# code is then the one-time code received back from google.
	print ("One-time auth code is: {}".format(code.decode()))
	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('google_client_secret.json', scope='') # this creates an oauth_flow object and adds the client_secrets info to it
		# client_secrets.json was the json object downloaded from console.developers.google.com for your app
		# needed to add some redirect uri s to the google api, and then re-download as it was causing errors.
		oauth_flow.redirect_uri = 'postmessage' # this specifies it is the one time code flow that the server will be sending off.
		credentials = oauth_flow.step2_exchange(code) # this initiates the exchange with the step2_exchange module, passing in the secret info.
		print ('\nSuccessfully updated the authorization code into a credentials object')
	# it exchanges the authorisation code for a credentials object. If all goes well, the response from Google will be a credentials object
	# that will be stored in the variable 'credentials'
	except FlowExchangeError:
		print ('FlowExchangeError triggered')
		print (FlowExchangeError)
		response = make_response(json.dumps('Failed to upgrade the authorization code'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid
	access_token = credentials.access_token
	print ('access_token is: %s' %access_token)
	url=('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
	# append the access token to the url and Google apiserver
	# will check to see if it is valid.
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1].decode())
	# If there was an error in the access token info, abort
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		print ('Access token info has no error')
		
	# Verify that the access token is used for the intended user:
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps("Token's user ID does not match given User ID"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		print ("Token's user ID MATCHES given User ID")

	# Verify that the access token is valid for this app
	if result['issued_to'] != GOOGLE_CLIENT_ID:
		response = make_response(
				json.dumps("Token's client ID does not match app's"),401)
		print ("Token's client ID does not match app's")
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		print("Token's client ID matches this current app's Google Client ID")

	# Check to see if user is already logged in
	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected'), 200)
		response.headers['Content-Type'] = 'application/json'

	# Assuming all the if statements are passed - you have not returned a response and the access token is valid

	# Store the access token in the session for later use
	login_session['provider'] = 'google'
	login_session['credentials'] = credentials
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
	params = {'access_token': credentials.access_token, 'alt':'json'}
	answer = requests.get(userinfo_url, params= params)
	data = json.loads(answer.text)

	login_session['username'] = data["name"]
	login_session['picture'] = data["picture"]
	login_session['email'] = data['email']

	# see if user exists in our database. If it doesn't, make a new one
	userId=getUserID(login_session['email'])
	if not userId:
		createUser(login_session)
	login_session['user_id'] = userId

	print(login_session)
	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += '"style="width: 300px; height: 300px; border-\
			radius: 150px;-webkit-border-radius: 150px;-moz-border-radius:150px;">'
	flash("you are now logged in as %s"%login_session['username'])
	print (output)
	return output


#DISCONNECT - Revoke a current user's token and reset their login_sesion
@app.route('/gdisconnect')
def gdisconnect():
	# Note that this is now supplemented by the generic /disconnect function
	print ('user attempting to gdisconnect - log out as google user')
	# only disconnect a connected user.
	credentials = login_session.get('credentials')
	if credentials is None:
		response = make_response(json.dumps('Current user not connected'), 401)
		response.headers['Content-Type']= 'application/json'
		return response
	# Execute HTTP GET request to REVOKE current token
	access_token = credentials.access_token
	# following url is googles url for revoking tokens
	url = "https://accounts.google.com/o/oauth2/revoke?token=%s" %access_token
	h = httplib2.Http()
	result = h.request(url, 'GET') [0]

	if result['status'] == '200':
		# Reset the user's session
		# These used to be deleted here, but now they are deleted in the generic disconnect function
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']

		response = make_response(json.dumps('Successfully disconnected'), 200)
		response.headers['Content-Type']= 'application/json'
		return response
	else:
		# for whatever reason, the given token was invalid
		response = make_response(json.dumps('Failed to revoke token for given user'), 400)
		response.headers['Content-Type']= 'application/json'
		return response

def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

def createUser(login_session):
    newUser = User(name = login_session['username'], email =
                   login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

@app.route('/catalog/<string:category>/items', methods=['GET'])
def category_display(category):
		# print ('category from GET request is {}'.format(category))
	category_requested = session.query(Category).filter_by(name = category).first()
	# pp.pprint (category_to_show.serialize)
	all_categories = session.query(Category).all()
	items_to_show = session.query(Item)\
									.filter_by(category_id = category_requested.id)\
									.order_by(Item.name).all()
	# for item in items_to_show:
		# pp.pprint (item.serialize)
	return render_template('category.html', categories = all_categories, \
													selected_category = category_requested.name, items = items_to_show)

@app.route('/catalog/<string:category>/<string:item>', methods=['GET'])
def item_display(category, item):
	# first get the item. Bear in mind there may be >1 e.g. rugby ball, soccer ball
	item_selected = session.query(Item).filter_by(name=item).all()
	category_selected = session.query(Category).filter_by(name=category).first()
	print (category_selected.name)
	for item in item_selected:
		if item.category_id == category_selected.id:
			# print (item.name)
			return render_template('item.html', item = item)

#--------------------------------------------------------
# Endpoints
@app.route('/api/categories', methods = ['GET'])
def categoriesJSON():
	categories = session.query(Category).all()
	return jsonify(CategoryList = [i.serialize for i in categories])

@app.route('/api/items', methods = ['GET'])
def itemsJSON():
	items = session.query(Item).all()
	return jsonify(ItemList = [i.serialize for i in items])

@app.route('/api/<string:category>/items/', methods=['GET'])
def categoryItemsJSON(category):
	category_selected = session.query(Category).filter_by(name = category).first()
	category_items = session.query(Item).filter_by(category_id = category_selected.id).all()
	return jsonify(CategoryItemList = [i.serialize for i in category_items])

#-------------------------------------------------------

if __name__ == "__main__":
	# createItem('goggles','protective eyewear', 3, 2)
	app.secret_key='super_secret_key_129847' # Required for sessions
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
