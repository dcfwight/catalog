from flask import Blueprint, request

dummy = Blueprint('dummy',__name__)

@dummy.route('/test', methods=['GET','POST'])
def dummy_test():
	if request.method =='GET':
		return'dummy/test GET received via Blueprint!'