"""WTForms"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError, DataRequired, Regexp, Length

from models import Playlist


class CreatePlaylistForm(FlaskForm):
  """Form for creating a playlist"""

  title = StringField("Playlist Title", description="My Playlist", validators=[InputRequired()])
  key = StringField("Playlist Password", description="bops", validators=[DataRequired(), Regexp(r'^[\w.@+-]+$',message='Key cannot have spaces'), Length(min=3, max=12)])

  def validate_key(self, key):
    """Check that the key is not already taken"""
    
    playlist = Playlist.query.filter_by(key=key.data.lower()).first() # Get phone number's first playlist
    # If playlist exists
    if playlist:
      raise ValidationError('Key is already taken!')
