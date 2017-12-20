import os
basedir = os.path.abspath(os.path.dirname(__name__))

USER = 'dougwight'
PASSWORD = 'Linton'
HOST = 'localhost'
PORT = 5432 # default port for postgresql
DATABASE = 'catalog'

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string camel176'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	
	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('POSTGRESQL_DATABASE_URI') or \
		'postgresql://{}:{}@{}:{}/{}'.format(USER,PASSWORD,HOST,PORT,DATABASE)
	
config = {
	'development': DevelopmentConfig,
	'default': DevelopmentConfig
}