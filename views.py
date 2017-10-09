from flask import Flask, jsonify, render_template, request, url_for

app = Flask(__name__)

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