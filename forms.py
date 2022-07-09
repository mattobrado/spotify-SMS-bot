"""WTForms"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

class UserForm(FlaskForm):
  """Form for signing up and logging in"""
  username = StringField("Username", validators=[InputRequired()])
  password = StringField("Password", validators=[InputRequired()])

class PlaylistForm(FlaskForm):
  """Form for creating a playlist"""
  title = StringField("Playlist Title", validators=[InputRequired()])