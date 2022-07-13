"""WTForms"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, ValidationError, DataRequired
import phonenumbers

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