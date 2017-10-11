from flask import Flask, flash, jsonify, redirect, render_template,\
		request, url_for
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
		flash('{} edited'.format(item_to_edit.name))
		return ('item with id: {} has been edited'.format(item_to_edit.id))

@app.route('/deleteCategory/<int:id>', methods = ['GET'])
def deleteCategory(id):
	category_to_delete = session.query(Category).filter_by(id=id).first()
	session.delete(category_to_delete)
	# We also need to delete the items associated with the category
	items_to_delete = session.query(Item).filter_by(category_id = id).all()
	if (items_to_delete):
		for item in items_to_delete:
			session.delete(item)
	session.commit()
	flash('{} deleted'.format(category_to_delete.name))
	return redirect(url_for('showCatalog'))

@app.route('/deleteItem/<int:id>', methods = ['GET'])
def deleteItem(id):
	item_to_delete = session.query(Item).filter_by(id = id).first()
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
	return render_template('category.html', category = category_to_show, \
				items = items_to_show)

if __name__ == "__main__":
	# createItem('goggles','protective eyewear', 3, 2)
	app.secret_key='super_secret_key' # Change this to a proper secret key later
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
