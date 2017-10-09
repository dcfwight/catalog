from flask import Flask, jsonify, render_template, request, url_for
import pprint as pp

app = Flask(__name__)

dummy_data = {'soccer':{
                'balls': {'desc':'round things that you can kick',
                          'time': 5,
                          'owner_id': 2},
                'nets': {'desc': 'stringy things that catch balls',
                         'time': 3,
                         'owner_id': 3}
                        },
            'rugby': {
                'balls': {'desc': 'oval things that you can carry OR kick',
                          'time': 1,
                          'owner_id': 1},
                'boots': {'desc': 'heavy, leathery things you wear on your feet',
                          'time': 7,
                          'owner_id': 2}
                    },
            'snowboarding': {
                'goggles': {'desc': 'protective screen for your eyes',
                            'time': 2,
                            'owner_id': 1},
                'snowboard': {'desc': 'Best for any terrain and condition. All-mountain snowboards blah ',
                              'time' : 4,
                              'owner_id': 3}
                    }
            }

@app.route('/', methods=['GET'])
@app.route('/catalog/', methods=['GET'])
def index():
    return render_template('catalog.html', data=dummy_data)


@app.route('/login/', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/catalog/<string:category>/', methods=['GET'])
def item(category):
    if dummy_data.get(category):
        return render_template('category.html', category=category, data = dummy_data[category])
    else:
        return render_template('catalog.html', data=dummy_data)


if __name__ == "__main__":
    app.secret_key='super_secret_key' # Change this to a proper secret key later
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
