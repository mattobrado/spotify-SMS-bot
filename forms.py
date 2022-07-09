"""WTForms"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

class UserForm(FlaskForm):
  username = StringField("Username", validators=[InputRequired()])
  password = StringField("Password", validators=[InputRequired()])
