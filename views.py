from flask import Flask, jsonify, render_template, request, url_for
import pprint as pp # for pretty-printing
# from collections import OrderedDict # to enable sorting on nested dictionaries

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

dummy_categories = {'soccer':{'id':1},
                    'rugby':{'id':2},
                    'snowboarding':{'id':3}
                    }

dummy_items = {
                'balls': {'desc':'round things that you can kick',
                          'time': 5,
                          'owner_id': 2,
                          'category_id': 1},
                'nets': {'desc': 'stringy things that catch balls',
                         'time': 3,
                         'owner_id': 3,
                         'category_id': 1},
                        
            
                'balls': {'desc': 'oval things that you can carry OR kick',
                          'time': 1,
                          'owner_id': 1,
                          'category_id': 2},
                'boots': {'desc': 'heavy, leathery things you wear on your feet',
                          'time': 7,
                          'owner_id': 2,
                          'category_id': 2},
                    
                'goggles': {'desc': 'protective screen for your eyes',
                            'time': 2,
                            'owner_id': 1,
                            'category_id': 3},
                'snowboard': {'desc': 'Best for any terrain and condition. All-mountain snowboards blah ',
                              'time' : 4,
                              'owner_id': 3,
                              'category_id': 3}
                   
            }

    

@app.route('/', methods=['GET'])
@app.route('/catalog/', methods=['GET'])    
def index():
    categories = session.query(Category).order_by(Category.name)
    for category in categories:
        pp.pprint(category.serialize)
    return render_template('catalog.html', categories=categories)


@app.route('/login/', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/catalog/<string:category>/', methods=['GET'])
def item(category):
    if category in dummy_categories:
        return render_template('category.html', category=category, data = dummy_data[category])
    else:
        return render_template('catalog.html', data=dummy_data)


if __name__ == "__main__":
    app.secret_key='super_secret_key' # Change this to a proper secret key later
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
