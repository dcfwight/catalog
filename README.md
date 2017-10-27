# Catalog project
Website to display categories and items in a catalog

## Aim of site
- Authorisation of users through use of third-party authenticators (Google & facebook)
- Use of CRUD functionality in accessing database
- Usage of Flask server and rendering web pages
- Usage of Bootstrap to create attractive front end

## Language
- Python3

## Installation
1. Clone the repository to your local computer
1. Install a virtual environment
1. Load the required modules into your virtual environment using requirements.txt
1. Set up the database with the command line script > python3 models.py
1. Run the server with the command line script > python3 views.py
1. The Flask server will now listen on port 5000. Open a browser and navigate to
[http://localhost:5000](http://localhost:5000)

## Usage
- Once the site is launched, you should be able to view categories and items
- You should be able to add / edit / delete items and categories, but ONLY after you have logged in with a third-party provider

## JSON API endpoints
3 api endpoints are set up which return the same info, in JSON format.
Note you will need to populate the database with a few items to make the APIs work

#####Categories
- [http://localhost:5000/api/v1.0/categories](http://localhost:5000/api/v1.0/categories)
- provides JSON object of all current categories
#####Items
- [http://localhost:5000/api/v1.0/items](http://localhost:5000/api/v1.0/items)
- provides JSON object of all items
#####Items in a category
- [http://localhost:5000/api/v1.0/:category/items](http://localhost:5000/api/v1.0/:category/items)
- provides JSON object of items in a category.
- e.g. localhost:5000/api/v1.0/hockey/items
####Specific item
- [http://localhost:5000/api/v1.0/:category/item](http://localhost:5000/api/v1.0/:category/item)
- provides JSON object on specific item
- NOTE you need to pass in category too - there may be two or more categories with "ball" as an item - e.g. golf, soccer.
- e.g. localhost:5000/api/v1.0/badminton/net

## To-Dos / Improvements
1. Add non-third-party authenticated logins (i.e. with username and password)
1. Create more forms rendered with flask_wtf (currently only create_category() uses it)
1. Abstract google and facebook logins into separate files, to simplify views.py and also
create re-usable login files for future work.
1. Unit-testing
1. Use of os.env variables to store app logins and passwords - more secure than fb_client_secret.json
and google_client_secret.json
1. Use of Flask-Mail to email with updates (e.g. problems / new users/ sending confirmation emails for new users)
1. Change application folder structure - use Flask blueprints
1. Rate-limiting
1. Use databse zips to combine two tables rather than current more convoluted sorting
1. Add self-populating database to allow for demonstration from initial loading.
1. Add in improved error-handling / reporting.

### Creator
Doug Wight, dcfwight@gmail.com

