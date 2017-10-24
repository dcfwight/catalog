from flask_wtf import FlaskForm
# Form class - allows for creation in Python, then rendered. Better validation
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
    name = StringField('Name: ', validators=[DataRequired()])
    submit = SubmitField('Submit')