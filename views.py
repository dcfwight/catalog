from flask import Flask, jsonify, render_template, request, url_for
import pprint as pp

app = Flask(__name__)

dummy_data = {'soccer':{
                'balls': 'round things that you can kick',
                'nets': 'stringy things that catch balls'},
              'rugby': {
                'balls': 'oval things that you can carry OR kick',
                'boots': 'heavy, leathery things you wear on your feet'
              },
              'snowboarding': {
                'goggles': 'protective screen for your eyes',
                'snowboard': 'Best for any terrain and condition. All-mountain snowboards blah '
              }
              }




@app.route('/', methods=['GET'])
@app.route('/catalog', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/categories', methods=['GET'])
def category():
    return render_template('category.html')

@app.route('/catalog/item', methods=['GET'])
def item():
    return render_template('item.html')


if __name__ == "__main__":
    app.secret_key='super_secret_key' # Change this to a proper secret key later
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)