from flask_wtf import FlaskForm
# Form class - allows for creation in Python, then rendered. Better validation
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length

class NameForm(FlaskForm):
    name = StringField('Name: ', validators=[InputRequired(),
                                             Length(max=32)])
    submit = SubmitField('Submit')