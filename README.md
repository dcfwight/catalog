# Catalog project
Postgresql server to display categories and items in a catalog running on localhost

## Functionality
- Creation of local postgresql database by running models.py. Has three different classes - User, Category, Item.
Updated to include postgresql
- Authentication of users through use of OAuth 2.0 third-party authenticators (Google & facebook)
- Authorisation of users to edit particular categories though database check.
- Use of CRUD functionality in accessing database
- Usage of Flask server and rendering web pages
- Usage of Bootstrap to create attractive front end
- Creation of JSON endpoints

## Installation of Postgresql - REQUIRED before running anything else!
- You will need to install Postgresql to your local computer or remote server.
- Follow the instructions on the [download page](https://www.postgresql.org/download/)
- You need this in place as both the setup program (models.py) and then the main program (manage.py) will
refer to the database stored in your Postgresql location.
- As of time of update, using a Mac, I downloaded Postgresql 14 to /Library/Postgresql/14
- During installation, you will be asked for a password for the superuser postgres.
- Postgresql will default to port 5432 when listening.
- A useful site for PostgreSQl setup is [here](https://www.prisma.io/dataguide/postgresql/setting-up-a-local-postgresql-database)
- Please refer to that site for important first stage set-up instructions to add the PostgreSQL bin directory to your
path, test it is working etc.
- Tutorials point site for PostgreSQL is [here](https://www.tutorialspoint.com/postgresql/postgresql_environment.htm)
- Tutorials point site for PostgreSQL set-up for Mac is [here](https://www.postgresqltutorial.com/install-postgresql-macos/)
- PostgreSQL documentation is found [here](https://www.postgresql.org/docs/current/index.html)

## Creation of new user in PostgreSQL - REQUIRED before running the server!
- You will need to create a new user and password within Postgresql.
- This will match the environment variables that you are going to set for the CATALOG_USER and CATALOG_PASS
  - see the section on environment variables below.
- However, you will also need to set these credentials up in PostgreSQL, otherwise it will not be able to 
access the database.
  - (shouldn't really use the default user, postgres)
- Log in as postgres:
  - `psql -U postgres`
- Fill in the password when prompted
- create a user with: 
  - `CREATE USER catalog_user WITH PASSWORD 'test123';`
- check the privileges with:
  - `\du`
  - You'll see they have no privileges.
- Amend the privileges with:
  - `ALTER USER catalog_user WITH SUPERUSER;`
- *Don't forget the ";" at the end of each line!*
- Useful youtube on set-up [here](https://www.youtube.com/watch?v=-LwI4HMR_Eg)
- 

## Use of PGAdmin
PG admin is a useful tool to examine your database, but I'm not going to fully detail it here.

## Language
- Python3


## Environment variables
- We will need passwords and usernames to access the postgresql database that will be set up.
- Bad practice to hard-code the username and password in the files
- Instead, store them in environment variables. An environment variable is a variable set outside the program, typically
built into the operating system.
- To get the environment variables into your system, edit the file at ~/.bash_profile with the following:
  - `export CATALOG_USER='catalog_user'`
  - `export CATALOG_PASS='Hamster246'`
- note there are no gaps around the '=' sign
- clearly, use your own names for the user and the  password, but note that they have to match

## Installation
1. Clone the repository to your local computer.
2. Install a virtual environment - e.g. `virtualenv venv`.
3. Activate the virtual environment - e.g. `source venv/bin/activate`
4. Make sure pip is up-to-date with `pip install --upgrade pip`
5. Load the required modules into your virtual environment using requirements.txt - e.g. `pip install -r requirements.txt`
6. Set up the database with the command line script `$ python3 models.py`
7. Run the server with the command line script: `$ python3 manage.py runserver -d`
8. The Flask server will now listen on port 5000. Open a browser and navigate to
[http://localhost:5000](http://localhost:5000)

## Usage
- Once the site is launched, you should be able to view categories and items
- You should be able to add / edit / delete items and categories, but ONLY after you have logged in with a third-party provider

## JSON API endpoints
3 api endpoints are set up which return the same info, in JSON format.
Note you will need to populate the database with a few items to make the APIs work

### Categories
- [http://localhost:5000/api/v1.0/categories](http://localhost:5000/api/v1.0/categories)
- provides JSON object of all current categories
### Items
- [http://localhost:5000/api/v1.0/items](http://localhost:5000/api/v1.0/items)
- provides JSON object of all items
### Items in a category
- [http://localhost:5000/api/v1.0/:category/items](http://localhost:5000/api/v1.0/:category/items)
- provides JSON object of items in a category.
- e.g. localhost:5000/api/v1.0/hockey/items
### Specific item
- [http://localhost:5000/api/v1.0/:category/item](http://localhost:5000/api/v1.0/:category/item)
- provides JSON object on specific item
- NOTE you need to pass in category too - there may be two or more categories with "ball" as an item - e.g. golf, soccer.
- e.g. localhost:5000/api/v1.0/badminton/net

## To-Dos / Improvements
1. Add non-third-party authenticated logins (i.e. with username and password)
1. Create more forms rendered with flask_wtf (currently only create_category() uses it)
1. Abstract google and facebook logins into separate files, to simplify views.py and also
create re-usable login files for future work.
1. Unit-testing.
1. Use of os.env variables to store app logins and passwords - more secure than fb_client_secret.json
and google_client_secret.json
1. Use of Flask-Mail to email with updates (e.g. problems / new users/ sending confirmation emails for new users)
1. Change application folder structure - use Flask blueprints
1. Rate-limiting
1. Use database zips to combine two tables rather than current more convoluted sorting
1. Add self-populating database to allow for demonstration from initial loading.
1. Take out debug print statements and put them in a log file.
1. Add in improved error-handling & reporting. 

## Sources used
- Udacity lecture videos, transcripts and notes
- O'Reilly book - "Flask Web Development" by Miguel Grinberg. Will use this a lot for implementing the improvements.

### Creator
Doug Wight, dcfwight@protonmail.com
