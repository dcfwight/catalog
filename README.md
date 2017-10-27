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
2. Install a virtual environment
3. Load the required modules into your virtual environment using requirements.txt
4. Run the server with the command line script > python3 views.py
5. The Flask server will now listen on port 5000. Open a browser and navigate to
[http://localhost:5000](http://localhost:5000)

## Usage
- Once the site is launched, you should be able to view categories and items
- You should be able to add / edit / delete items and categories, but ONLY after you have logged in with a third-party provider

### To-Dos / Improvements
1. Add non-third-party authenticated logins (i.e. with username and password)
2. Create more forms rendered with flask_wtf (currently only create_category() uses it)
3. Abstract google and facebook logins into separate files, to simplify views.py and also
create re-usable login files for future work.
4. Unit-testing
5. Use of os.env variables to store app logins and passwords - more secure than fb_client_secret.json
and google_client_secret.json
6. Use of Flask-Mail to email with updates (e.g. problems / new users/ sending confirmation emails for new users)
7. Change application folder structure - use Flask blueprints

### Creator
Doug Wight, dcfwight@gmail.com

