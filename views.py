from flask import Flask, jsonify, render_template, request, url_for
import pprint as pp # for pretty-printing
# from collections import OrderedDict # to enable sorting on nested dictionaries

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item
import time

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

dummy_categories = {
	'soccer':{'id':1},
	'rugby':{'id':2},
	'snowboarding':{'id':3}
}

dummy_items = {
	'balls': {
		'desc':'round things that you can kick',
		'time': 5,
		'owner_id': 2,
		'category_id': 1
	},
	'nets': {
		'desc': 'stringy things that catch balls',
		'time': 3,
		'owner_id': 3,
		'category_id': 1
	},
	'balls': {
		'desc': 'oval things that you can carry OR kick',
		'time': 1,
		'owner_id': 1,
		'category_id': 2
	},
	'boots': {
		'desc': 'heavy, leathery things you wear on your feet',
		'time': 7,
		'owner_id': 2,
		'category_id': 2
	},
	'goggles': {
		'desc': 'protective screen for your eyes',
		'time': 2,
		'owner_id': 1,
		'category_id': 3
	},
	'snowboard': {
		'desc': 'Best for any terrain and condition. All-mountain snowboards blah ',
		'time' : 4,
		'owner_id': 3,
		'category_id': 3
	}
}


@app.route('/', methods=['GET'])
@app.route('/catalog/', methods=['GET'])
def showCatalog():
	categories = session.query(Category).order_by(Category.name)
	for category in categories:
		pp.pprint(category.serialize)
	print (int(time.time()))
	items = session.query(Item).all()
	return render_template('catalog.html', categories=categories,
							items = items)

@app.route('/createItem/', methods=['POST'])
def createItem(name, description, category_id, user_id):
	create_time = int(time.time())
	newItem = Item(name = name, description = description,
		category_id = category_id, user_id = user_id,
		create_time = create_time)
	session.add(newItem)
	session.commit()

@app.route('/editItem/<int:id>', methods=['POST'])	
def editItem(id):
	if request.method=='POST':
		item_to_edit = session.query(Item).filter_by(id = id).one()
		print ('item to edit retrieved from database')
		pp.pprint (item_to_edit.serialize)
		if request.form['name']:
			item_to_edit.name = request.form['name']
		if request.form['description']:
			item_to_edit.description = request.form['description']
		if request.form['category_id']:
			item_to_edit.description = request.form['category_id']
		if request.form['user_id']:
			item_to_edit.description = request.form['user_id']
		for key in request.form:
			print(key, ': ', request.form[key] )
		session.add(item_to_edit)
		session.commit()
		return ('item with id: {} has been edited'.format(item_to_edit.id))

@app.route('/login/', methods=['GET'])
def login():
	return render_template('login.html')

@app.route('/catalog/<string:category>/', methods=['GET'])
def item(category):
	if category in dummy_categories:
		return render_template('category.html', category=category,
			data = dummy_data[category])
	else:
		return render_template('catalog.html', data=dummy_data)

if __name__ == "__main__":
	# createItem('goggles','protective eyewear', 3, 2)
	app.secret_key='super_secret_key' # Change this to a proper secret key later
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
