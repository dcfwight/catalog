import random
import string
import pprint
import json
import time
import logging

from flask import Flask, flash, jsonify, redirect, render_template
from flask import request, url_for
from flask import session as login_session
# session is a dictionary that stores users login details
# for the duration of their session
from flask import make_response #converts the return value from a function
# into a real response object to send to client

from flask_script import Manager #Adds a command-line parser

# from flask import Blueprint

from flask_bootstrap import Bootstrap
# flask Boostrap extension to help with implementing Bootstrap.

from forms import NameForm

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item

from oauth2client.client import flow_from_clientsecrets
# creates a flow objectfrom clientsecrets JSON file.
# Stores client Id and other oAuth parameters
from oauth2client.client import FlowExchangeError
# this will catch errors when trying to exchange
# an authorisation code for an access token.
from oauth2client.client import AccessTokenCredentials
# this is required to fix Oauth error with JSON objects

import httplib2 # comprehensive http clientlibrary in python

import requests

pp = pprint.PrettyPrinter(indent=4)
logging.basicConfig(filename='catalog.log', level=logging.DEBUG,
	format='%(asctime)s %(message)s')

GOOGLE_CLIENT_ID = json.loads(open('google_client_secret.json', 'r')
							  .read())['web']['client_id']

user = 'dougwight'
password = 'Linton'
host = 'localhost'
port = 5432 # default port for postgresql
database = 'catalog'

url = 'postgresql://{}:{}@{}:{}/{}'.format(user,password,host,port,database)

engine = create_engine(url, client_encoding='utf8')

# This was the previous method of storing to an sqlite database - now using postgresql
# engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Blueprint
# from routes.dummy import dummy # this is a test one for Blueprints
# from routes.login import login

app = Flask(__name__)
bootstrap = Bootstrap(app)
manager = Manager(app)


@app.route('/', methods=['GET'])
@app.route('/catalog/', methods=['GET'])
def show_catalog():
	'''returns Catalog template'''
	categories = session.query(Category).order_by(func.lower(Category.name))
	items = session.query(Item).order_by(Item.edited_time.desc()).limit(5)
	latest_items = []
	for item in items:
		latest_items.append(item.serialize)
	for item in latest_items:
		item['category_name'] = (session.query(Category)
								 .filter_by(id=item['category_id'])
								 .one().name)
	return render_template('catalog.html', categories=categories,
						   latest_items=latest_items)

@app.route('/catalog/<string:category>/items', methods=['GET'])
def category_display(category):
	'''returns category template'''
	category_requested = (session.query(Category)
						  .filter_by(name=category)
						  .first())
	logging.info('category requested: {}'.format(category))
	logging.info('category returned from database:')
	logging.info(category_requested.serialize)
	all_categories = session.query(Category).order_by(Category.name)
	
	items_to_show = (session.query(Item)
					 .filter_by(category_id=category_requested.id)
					 .order_by(Item.name).all())
	
	logging.info('items to show:')
	for item in items_to_show:
		logging.info(item.serialize)
	return render_template('category.html',
						   categories=all_categories,
						   selected_category=category_requested,
						   items=items_to_show)

@app.route('/catalog/<string:category>/<string:item>', methods=['GET'])
def item_display(category, item):
	'''returns item template'''
	# first get the item. Bear in mind there may be >1
	# e.g. rugby ball, soccer ball
	item_selected = session.query(Item).filter_by(name=item).all()
	logging.info('Query database on category: {}'.format(category))
	category_selected = (session.query(Category)
						 .filter_by(name=category)
						 .first())

	for item in item_selected:
		if item.category_id == category_selected.id:
			return (render_template('item.html',
									item=item, category=category))

@app.route('/create_category/', methods=['GET', 'POST'])
def create_category():
	'''handles creation of a new category'''
	# This function uses the Flask-wtf form, to demonstrate it. The others don't
	# again, to demonstrate the different methods.
	form = NameForm()
	if form.validate_on_submit() and 'username' in login_session:
		category_name = form.name.data
		if session.query(Category).filter_by(name=category_name).first():
			flash('Category: {} already exits'.format(category_name))
		else:
			new_category = Category(name=category_name,
									creator_id=login_session['user_id'])
			session.add(new_category)
			session.commit()
			flash('{} created'.format(new_category.name))
	elif 'username' in login_session:
		# i.e. we have a logged in user, so go to createCategory.html
		return render_template('createCategory.html', form=form)
	else:
		flash('You need to login first to create a Category')
		return render_template('login.html')
	return redirect(url_for('show_catalog'))

@app.route('/createItem/', methods=['GET','POST'])
def create_item_no_category():
	"""creates an Item, when there is no category selected"""
	if 'username' in login_session:
		# user is logged in, so render the createItem page
		categories = session.query(Category).all()
		return render_template('createItem.html',
							   categories=categories,
							   selected_category='')
	else:
		# user is NOT logged in, so render the loginpage
		flash('You need to login first to create a new item.')
		return render_template('login.html')

@app.route('/<string:category>/createItem/', methods=['GET', 'POST'])
def create_item(category):
	'''handles creation of a new Item'''
	if request.method == 'GET' and 'username' in login_session:
		# user is logged in, so render the createItem page
		categories = session.query(Category).all()
		return render_template('createItem.html',
							   categories=categories,
							   selected_category=category)
	elif request.method == 'GET':
		# user is NOT logged in, so render the loginpage
		flash('You need to login first to create a new item.')
		return render_template('login.html')
	elif request.method == 'POST':
		
		new_item = Item()
		if request.form['name']:
			new_item.name = request.form['name']
		if request.form['description']:
			new_item.description = request.form['description']
		category_selected = (session.query(Category)
							.filter_by(name=request.form['category'])
							.one())
		new_item.category_id = category_selected.id
		new_item.creator_id = login_session['user_id']
		
		new_item.edited_time = int(time.time())
		session.add(new_item)
		session.commit()
		flash('{} created'.format(new_item.name))
		return redirect(url_for('category_display',
								category=category_selected.name))

@app.route('/<string:category>/edit/', methods=['GET', 'POST'])
def edit_category(category):
	'''handles editing of an existing category'''
	category_to_edit = (session.query(Category)
						.filter_by(name=category)
						.first())
	if request.method == 'GET':
		if not login_session['user_id']:
			flash('You need to log in to edit a Category')
			return redirect(url_for('login'))
		elif login_session['user_id'] == category_to_edit.creator_id:
			return render_template('editCategory.html',
								   category=category_to_edit.name)
		else:
			flash('You cannot edit the Category as you are not its creator')
			return redirect(url_for('category_display', category=category))
	if request.method == 'POST':
		
		if request.form['name']:
			category_to_edit.name = request.form['name']
		session.add(category_to_edit)
		session.commit()
		flash('{} edited'.format(category_to_edit.name))
		return redirect(url_for('category_display',
								category=category_to_edit.name))

@app.route('/<string:category>/delete/', methods=['GET', 'POST'])
def delete_category(category):
	'''handles deletion of an existing category'''
	category_to_delete = (session.query(Category)
						  .filter_by(name=category)
						  .first())
	if request.method == 'GET':
		if not login_session['user_id']:
			flash('You need to log in to delete a Category')
			return redirect(url_for('login'))
		elif login_session['user_id'] == category_to_delete.creator_id:
			return render_template('deleteCategory.html',
								   category=category_to_delete)
		else:
			flash('You cannot delete the Category as you are not its creator')
			return redirect(url_for('category_display', category=category))
	if request.method == 'POST':
		
		if not login_session['user_id']:
			flash('You need to log in to delete a Category')
			return redirect(url_for('login'))
		elif login_session['user_id'] != category_to_delete.creator_id:
			flash('You need to be the Category creator to delete it')
			return redirect(url_for('show_catalog'))
		else:
			# first we also need to delete all items under this parent category
			items_to_delete = (session.query(Item)
							   .filter_by(category_id=category_to_delete.id)
							   .all())
			for item in items_to_delete:
				session.delete(item)
				session.commit()
			session.delete(category_to_delete)
			session.commit()
			flash('{} deleted'.format(category_to_delete.name))
			return redirect(url_for('show_catalog'))

@app.route('/<string:category_name>/<string:item_name>/edit_item/',
		   methods=['GET', 'POST'])
def edit_item(category_name, item_name):
	'''handles editing of an existing item'''
	potential_items = (session.query(Item)
					   .filter_by(name=item_name).all())
	category_selected = (session.query(Category)
						 .filter_by(name=category_name).first())
	item_to_edit = []
	for item in potential_items:
		if item.category_id == category_selected.id:
			item_to_edit = item
	logging.info('item to edit retrieved from database')
	logging.info(item_to_edit.serialize)
	logging.info("item_to_edit['name'] is: {}".format(item_to_edit.serialize['name']))
	edited_time = int(time.time())
	if request.method == 'GET':
		return render_template('editItem.html',
							   item=item_to_edit.serialize,
							   category=category_selected)
	elif request.method == 'POST' and (login_session['user_id']
									   != item_to_edit.creator_id):
		flash('You cannot edit that item - only the creator can edit')
		return redirect(url_for('category_display',
								category=category_selected.name))
	elif request.method == 'POST' and (login_session['user_id']
									   == item_to_edit.creator_id):
		if request.form['name']:
			item_to_edit.name = request.form['name']
		if request.form['description']:
			item_to_edit.description = request.form['description']
		
		if request.form != []:
			item_to_edit.edited_time = edited_time
		session.add(item_to_edit)
		session.commit()
		flash('{} edited'.format(item_to_edit.name))
		return redirect(url_for('item_display', category=category_selected.name,
								item=item_to_edit.name))
	else:
		console.log('error in edit_item code')

@app.route('/<string:category_name>/<string:item_name>/deleteItem/',
		   methods=['GET', 'POST'])
def delete_item(category_name, item_name):
	'''handles deletion of an existing item'''
	potential_items = session.query(Item).filter_by(name=item_name).all()
	category_selected = (session.query(Category)
						 .filter_by(name=category_name).first())
	item_to_delete = []
	for item in potential_items:
		if item.category_id == category_selected.id:
			item_to_delete = item

	if request.method == 'GET':
		return render_template('deleteItem.html',
							   item=item_to_delete, category=category_selected)
	elif request.method == 'POST' and (login_session['user_id']
									   != item_to_delete.creator_id):
		flash('You cannot edit that item - only the creator can delete')
		return redirect(url_for('category_display', category=category_name))

	elif request.method == 'POST' and (login_session['user_id']
									   == item_to_delete.creator_id):
		session.delete(item_to_delete)
		session.commit()
		flash('{} deleted'.format(item_to_delete.name))
		return redirect(url_for('category_display', category=category_name))
	else:
		logging.error('error in deleteItem code')

@app.route('/login/', methods=['GET'])
def login():
	'''returns login template'''
	# first create an anti-forgery state token which is long and random
	state = (''.join(random.choice(string.ascii_uppercase + string.digits)
					 for x in range(32)))
	login_session['state'] = state
	# if we have a previous 'state', it will be over-written
	return render_template('login.html', STATE=login_session['state'])

@app.route('/gconnect', methods=['POST'])
def gconnect():
	'''handles approval of google oauth'''
	print('POST /gconnect received')
	# Validate the state token
	if request.args.get('state') != login_session['state']:
		print('login_session["state"] was: {}'
			  .format(login_session['state']))
		print('request.args.get("state") was: {}'
			  .format(request.args.get('state')))

		print('invalid state parameter')
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# If it passes that, then we next obtain a one-time authorisation code.
	print("state parameter was valid. Obtaining a one-time authorisation code")
	code = request.data
	# this will only happen if the if statement above is false
	# i.e. IFF the state variable matches correctly.
	# code is then the one-time code received back from google.
	print("\nGoogle One-time auth code is: {}".format(code.decode()))
	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('google_client_secret.json',
											 scope='')
		# creates an oauth_flow object and adds the client_secrets info to it
		# client_secrets.json was the json object downloaded from
		# console.developers.google.com for your app
		# needed to add some redirect uri s to the google api,
		# and then re-download as it was causing errors.
		oauth_flow.redirect_uri = 'postmessage'
		# this specifies it is the one time code flow
		# that the server will be sending off.
		credentials = oauth_flow.step2_exchange(code)
		# this initiates the exchange with the step2_exchange module,
		# passing in the secret info.
		print('\nGoogle: Successfully updated the authorization code into'
			  'a credentials object')
		# it exchanges the authorisation code for a credentials object.
		# If all goes well the response from Google will be a credentials object
		# that will be stored in the variable 'credentials'
	except FlowExchangeError:
		logging.error('FlowExchangeError triggered')
		logging.error(FlowExchangeError)
		response = make_response(json.dumps(
			'Failed to upgrade the authorization code'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid
	access_token = credentials.access_token
	logging.info('Google access_token is: {}'.format(access_token))
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'
		   .format(access_token))
	# append the access token to the url and Google apiserver
	# will check to see if it is valid.
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1].decode())
	# If there was an error in the access token info, abort
	if result.get('error') is not None:
		logging.error('There was an error in the Google Access token')
		logging.error(result['error'])
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		logging.info('Google Access token info has no error')

	# Verify that the access token is used for the intended user:
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps(
			"Token's user ID does not match given User ID"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		logging.info("Token's user ID MATCHES given User ID")

	# Verify that the access token is valid for this app
	if result['issued_to'] != GOOGLE_CLIENT_ID:
		response = make_response(
			json.dumps("Google Token's client ID does not match app's"), 401)
		logging.error("Google Token's client ID does not match app's")
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		logging.info("Google Token's client ID matches this current app's\
			  Google Client ID")

	# Check to see if user is already logged in
	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps(
			'Current user is already connected'), 200)
		response.headers['Content-Type'] = 'application/json'

	# Assuming all the if statements are passed - you have not returned
	# a response and the access token is valid

	# Store the access token in the session for later use
	login_session['provider'] = 'google'

	login_session['credentials'] = credentials.access_token
	# NOTE this is different to Udacity course - storing only the access token
	# Not entirely sure why - see https://github.com/udacity/ud330/issues/4
	# for discussion. Post by Linus Dong fixed it.
	# return credential object
	credentials = AccessTokenCredentials(
		login_session['credentials'], 'user-agent-value')
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
	params = {'access_token': credentials.access_token, 'alt':'json'}
	answer = requests.get(userinfo_url, params=params)
	data = json.loads(answer.text)
	logging.info("\nGoogle user info is: ")
	logging.info(data)

	login_session['username'] = data["name"]
	login_session['picture'] = data["picture"]
	login_session['email'] = data['email']

	# see if user exists in our database. If it doesn't, make a new one
	user_id = get_user_id(login_session['email'])
	if not user_id:
		user_id=create_user(login_session)
		logging.info('User was NOT in database, so user was created')
	else:
		logging.info('User was already in database, so no changes made')
		login_session['user_id'] = user_id

	logging.info('login_session is: {}'.format(login_session))
	logging.info("login_session['user_id'] is: {}".format(login_session['user_id']))

	return login_welcome(login_session['username'], login_session['picture'])

def login_welcome(username, picture=''):
	'''returns login welcome template, using users information'''
	output = ''
	# output += '<div class="container">
	output += '<div class="row"><div class="col-md-6">'
	output += '<h1>Welcome, '
	output += username
	output += '!</h1>'
	output += '</div><div class="col-md-6">'
	if picture:
		output += '<img src="'
		output += picture
		output += '"style="width: 250px; height: 250px; border-\
			radius: 50px;-webkit-border-radius: 150px;\
			-moz-border-radius:150px;">'
	output += '</div>'
	output += '</div>'
	output += '<div class="row"><div class="col-md-12">\
			  <h2>Redirecting.....</h2></div></div>'
	flash("you are now logged in as {}".format(login_session['username']))
	# print(output)
	return output

#DISCONNECT - Revoke a current user's token and reset their login_sesion
@app.route('/gdisconnect')
def gdisconnect():
	'''disconnects user authenticated by google and removes information'''
	# Note that this is now supplemented by the generic /disconnect function
	logging.info('user attempting to gdisconnect - log out as google user')
	# only disconnect a connected user.
	credentials = login_session.get('credentials')
	logging.info('login_session.get("credentials") is: {}'.format(credentials))
	
	if credentials is None:
		response = make_response(json.dumps('Current user not connected'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Execute HTTP GET request to REVOKE current token
	# access_token = credentials.access_token
	# previous line no longer relevant, once we fixed the issue (search this
	# file for comments on Linus Dong to see where it was fixed)
	# following url is google's url for revoking tokens
	url = ("https://accounts.google.com/o/oauth2/revoke?token={}"
		   .format(credentials))
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	if result['status'] == '200':
		return {'message': 'Successfully disconnected',
				'status': 200}
	else:
		logging.error('Failed to revoke token for given user')
		return {'message':'Failed to revoke token for given user',
				'status': 400}
	

################################################################################
## FACEBOOK connection ##

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
	'''Handles authentication of user via facebook oauth'''
	# validate state token sent by client.
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	access_token = request.data.decode()
	# print('facebook short-lived access token is: {}'.format(access_token))

	# Retrieve the app_id and app_secret from our fb_client_secret file
	app_id = json.loads(open('fb_client_secret.json', 'r')
						.read())['web']['app_id']
	app_secret = json.loads(open('fb_client_secret.json', 'r')
							.read())['web']['app_secret']

	# Exchange client token for long-lived server-side token
	url = ('https://graph.facebook.com/v2.9/oauth/access_token?'
		   'grant_type=fb_exchange_token&client_id={}&client_secret={}'
		   '&fb_exchange_token={}'.format(app_id, app_secret, access_token))
	# print('facebook url to send to get exchange token is: ')
	# print(url)
	h = httplib2.Http()
	result = h.request(url, 'GET')[1].decode()
	fb_ll_token = json.loads(result)
	logging.info('\nFacebook long-lived server-side token is: {}'.format(fb_ll_token))
	
	token_string = 'access_token='+fb_ll_token['access_token']

	# The access token must be stored in the login session in order to
	# properly log out. NOTE this was a change from original Udacity lecture
	# code, as Facebook updated API required access code to be sent when
	# revoking the access token.
	login_session['access_token'] = fb_ll_token['access_token']

	#use token to get user info from API
	userinfo_url = ('https://graph.facebook.com/v2.8/me?{}'
					'&fields=name,id,email'.format(token_string))
	h = httplib2.Http()
	result = h.request(userinfo_url, 'GET')[1].decode()

	data = json.loads(result)
	logging.info('\nFacebook User info is: {}'.format(data))
	
	login_session['provider'] = 'facebook'
	login_session['username'] = data["name"]
	login_session['email'] = data['email']
	login_session['facebook_id'] = data["id"]



	# Get user picture
	# facebook uses a seperate API call to get user picture
	url = ('https://graph.facebook.com/v2.2/me/'
		   'picture?{}&redirect=0&height=200&width=200'.format(token_string))
	h = httplib2.Http()
	result = h.request(url, 'GET')[1].decode()
	data = json.loads(result)

	logging.info('Facebook: result from user picture request is: ')

	login_session['picture'] = data['data']['url']

	# see if user exists in our database. If it doesn't, make a new one
	userId = get_user_id(login_session['email'])
	if not userId:
		create_user(login_session)
	login_session['user_id'] = userId

	return login_welcome(login_session['username'], login_session['picture'])

@app.route('/fbdisconnect')
# Note that this is now supplemented by the generic /disconnect function
def fbdisconnect():
	'''Disconnects user authenticated by facebook'''
	facebook_id = login_session['facebook_id']
	access_token = login_session['access_token']
	# Note the following url changed from original Udacity code, because
	# facebook updated API call and requested the access_token as well.
	url = ('https://graph.facebook.com/{}/permissions'
		   '?access_token={}'.format(facebook_id, access_token))

	h = httplib2.Http()
	result = json.loads(h.request(url, 'DELETE')[1].decode())
	pp.pprint(result)
	# NB the deletions for lognin_session are all handled in disconnect()
	if result['success']:
		
		logging.info('Facebook logout completed successfully')
		return "you have been logged out"
	else:
		logging.error("error in logging out")
		return "error in logging out"

@app.route('/disconnect')
def disconnect():
	'''Generic disconnect - removes user info, according to authenticator'''
	if 'provider' in login_session:
		if login_session['provider'] == 'google':
			response = gdisconnect()
			if response['status'] == 400:
				print(response['message'])
			del login_session['gplus_id']
			del login_session['credentials']
		if login_session['provider'] == 'facebook':
			response = fbdisconnect()
			print(response)
			del login_session['facebook_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		del login_session['user_id']
		del login_session['provider']
		flash("You have been successfully logged out")
		return redirect(url_for('show_catalog'))
	else:
		flash("You were not logged in to begin with!")
		return redirect(url_for('show_catalog'))


def get_user_id(email):
	'''return user.id based on email'''
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		logging.error('error occured on retrieving user.id')
		return None

def get_user_info(user_id):
	'''return user based on user_id'''
	user = session.query(User).filter_by(id=user_id).one()
	return user

def create_user(login_session):
	'''Creates new user and inserts into database'''
	new_user = User(username=login_session['username'],
					email=login_session['email'],
					picture=login_session['picture'])
	session.add(new_user)
	session.commit()
	user = (session.query(User)
			.filter_by(email=login_session['email'])
			.one())
	return user.id



#--------------------------------------------------------
# Endpoints
@app.route('/api/v1.0/categories', methods=['GET'])
def categories_json():
	'''returns API endpoint of categories'''
	categories = session.query(Category).all()
	return jsonify(CategoryList=[i.serialize for i in categories])

@app.route('/api/v1.0/items', methods=['GET'])
def items_json():
	'''returns API endpoint of all items'''
	items = session.query(Item).all()
	return jsonify(ItemList=[i.serialize for i in items])

@app.route('/api/v1.0/<string:category>/items/', methods=['GET'])
def category_items_json(category):
	'''returns API endpoint of all items by Category'''
	category_selected = (session.query(Category)
						 .filter_by(name=category)
						 .first())
	category_items = (session.query(Item)     
					  .filter_by(category_id=category_selected.id)
					  .all())
	return jsonify(CategoryItemList=[i.serialize for i in category_items])

@app.route('/api/v1.0/<string:category>/<string:item>', methods=['GET'])
def category_item_json(category, item):
	'''returns API endpoint of item in category'''
	category_selected = (session.query(Category)
						 .filter_by(name=category)
						 .first())
	pp.pprint(category_selected.serialize)
	items_selected = (session.query(Item).filter_by(name=item).all())
	for i in items_selected:
		if i.category_id == category_selected.id:
			return jsonify(i.serialize)   
	return ('could not find item {} in category {}'
			.format(item, category))

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	app.secret_key = 'X7Sm23k39lsGGvD0XcMMkcwoH8cW2fkr1fgDzXK9D8S2V050'
	# Required for sessions
	print('Server running on localhost:5000/')
	manager.run()
