from flask import Flask, jsonify, request, url_for

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/catalog', methods=['GET'])
def main():
    return ('Catalog Home page')

@app.route('/login', methods=['GET'])
def login():
    return ('Login screen requested')

if __name__ == "__main__":
    app.secret_key='super_secret_key' # Change this to a proper secret key later
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)