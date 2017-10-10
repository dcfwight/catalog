from flask import Flask, jsonify, render_template, request, url_for, redirect
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

@app.route('/', methods=['GET'])
@app.route('/catalog/', methods=['GET'])
def showCatalog():
	categories = session.query(Category).order_by(Category.name)
	for category in categories:
		pp.pprint(category.serialize)
	items = session.query(Item).all()
	return render_template('catalog.html', categories=categories,
							items = items)

@app.route('/createCategory/', methods = ['POST'])
def createCategory():
	# print (request.form)
	if request.method =='POST':
		category_name = request.form['name']
		if session.query(Category).filter_by(name = category_name).first():
			return ('Category already exists')
		else:
			newCategory = Category(name=category_name)
			session.add(newCategory)
			session.commit()
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
	return jsonify(newItem.serialize)
	


@app.route('/editItem/<int:id>', methods=['POST'])	
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
		return ('item with id: {} has been edited'.format(item_to_edit.id))

@app.route('/login/', methods=['GET'])
def login():
	return render_template('login.html')

@app.route('/catalog/<string:category>/', methods=['GET'])
def category_display(category):
	# print ('category from GET request is {}'.format(category))
	category_to_show = session.query(Category).filter_by(name = category).first()
	# pp.pprint (category_to_show.serialize)
	items_to_show = session.query(Item)\
		.filter_by(category_id = category_to_show.id)\
		.order_by(Item.name).\
		all()
	# for item in items_to_show:
		# pp.pprint (item.serialize)
	return render_template('category.html', category = category_to_show,
						   items = items_to_show)

if __name__ == "__main__":
	# createItem('goggles','protective eyewear', 3, 2)
	app.secret_key='super_secret_key' # Change this to a proper secret key later
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
