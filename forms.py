"""WTForms"""
from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError
from wtforms.validators import InputRequired
import phonenumbers

class PhoneNumberForm(FlaskForm):
  phone_number = StringField("Your phone number", validators=[InputRequired()])

  def validate_phone(form, field):
    if len(field.data) > 16:
      raise ValidationError('Invalid phone number.')
    try:
      input_number = phonenumbers.parse(field.data)
      if not (phonenumbers.is_valid_number(input_number)):
        raise ValidationError('Invalid phone number.')
    except:
      input_number = phonenumbers.parse("+1"+field.data)
      if not (phonenumbers.is_valid_number(input_number)):
          raise ValidationError('Invalid phone number.')

class PlaylistForm(FlaskForm):
  """Form for creating a playlist"""
  title = StringField("Playlist Title", validators=[InputRequired()])
  tag = StringField("Playlist Tag (#my_sms_playlist)", validators=[InputRequired()])