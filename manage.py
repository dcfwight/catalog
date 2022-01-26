#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Category, Item
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

# Having to import the database instance and models each time a shell session is
# started is tedious work. To avoid having to constantly repeat these imports, the
# Flask-Script's shell command can be configured to import certain objects
# To add objects to the import list, the shell command needs to be registered
# with a make_context callback function

# To run this, enter python manage.py shell at command line


def make_shell_context():
	return dict(app=app, db=db, User=User, Category=Category, Item=Item)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
	manager.run()
