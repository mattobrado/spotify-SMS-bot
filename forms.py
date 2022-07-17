"""WTForms"""

from selectors import SelectSelector
from click import secho
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import InputRequired, ValidationError, DataRequired, Regexp, Length
from wtforms_sqlalchemy.fields import QuerySelectField
import phonenumbers

from models import Playlist


class PhoneForm(FlaskForm):
  """PhoneForm was provided by Twilio"""

  phone = StringField('Phone', validators=[DataRequired()])
  submit = SubmitField('Submit')

  def validate_phone(self, phone):
    try:
      p = phonenumbers.parse(phone.data)
      if not phonenumbers.is_valid_number(p):
        raise ValueError()
    except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
      raise ValidationError('Invalid phone number')


class CreatePlaylistForm(FlaskForm):
  """Form for creating a playlist"""

  title = StringField("New Playlist Title", validators=[InputRequired()])
  key = StringField("Playlist Password. Your friends will use this to add tracks", validators=[DataRequired(), Regexp(r'^[\w.@+-]+$'), Length(min=3, max=12)])

  def validate_key(self, key):
    """Check that the key is not already taken"""
    
    playlist = Playlist.query.filter_by(key=key.data.lower()).first() # Get phone number's first playlist
    # If playlist exists
    if playlist:
      raise ValidationError('Key is already taken!')


class SelectPlaylistForm(FlaskForm):
  """Form for seclecting a playlist to view"""

  # host_user_id = StringField()

  playlist = SelectField('Select Playlist', description="test")
  # submit= SubmitField()

def load_select_playlist_form_choices(host_user):
  """Populate Seclect Playlist form with choices"""

  select_form = SelectPlaylistForm() # Form for making a new playlist

  choices = [("","Select Playlist")]
  for playlist in host_user.playlists:
    choices.append((playlist.id, f"{playlist.title} #{playlist.key}"))
  select_form.playlist.choices = choices

  return select_form