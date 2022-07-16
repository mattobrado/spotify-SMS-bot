"""WTForms"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, ValidationError, DataRequired, Regexp, Length
import phonenumbers

from models import Playlist

# PhoneForm was provided by Twilio
class PhoneForm(FlaskForm):
  phone = StringField('Phone', validators=[DataRequired()])
  submit = SubmitField('Submit')

  def validate_phone(self, phone):
    try:
      p = phonenumbers.parse(phone.data)
      if not phonenumbers.is_valid_number(p):
        raise ValueError()
    except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
      raise ValidationError('Invalid phone number')

class PlaylistForm(FlaskForm):
  """Form for creating a playlist"""
  title = StringField("Playlist Title", validators=[InputRequired()])
  key = StringField("Playlist Key. Your friends will use this key to add tracks", validators=[DataRequired(), Regexp(r'^[\w.@+-]+$'), Length(min=3, max=12)])

  def validate_key(self, key):
    """Check that the key is not already taken"""
    
    playlist = Playlist.query.filter_by(key=key.data.lower()).first() # Get phone number's first playlist
    # If playlist exists
    if playlist:
      raise ValidationError('Key is already taken!')
    