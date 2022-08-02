"""WTForms"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
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


class SelectPlaylistForm(FlaskForm):
  """Form for seclecting a playlist to view"""

  playlist = SelectField('Select Playlist', description="test")

def load_select_playlist_form_choices(host_user):
  """Populate Seclect Playlist form with choices"""

  select_form = SelectPlaylistForm() # Form for making a new playlist

  choices = [("","Select Playlist")]
  for playlist in host_user.playlists:
    choices.append((playlist.id, f"{playlist.title} #{playlist.key}"))
  select_form.playlist.choices = choices

  return select_form