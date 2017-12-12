from flask import Blueprint, request
from flask import session as login_session
import random

login = Blueprint('login',__name__)

@login.route('/', methods=['GET'])
def login():
	'''returns login template'''
	# first create an anti-forgery state token which is long and random
	state = (''.join(random.choice(string.ascii_uppercase + string.digits)
					 for x in range(32)))
	login_session['state'] = state
	# if we have a previous 'state', it will be over-written
	return render_template('login.html', STATE=login_session['state'])