"""WTForms"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired

class PlaylistForm(FlaskForm):
  """Form for creating a playlist"""
  title = StringField("Playlist Title", validators=[InputRequired()])