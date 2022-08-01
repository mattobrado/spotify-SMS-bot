"""Forms for authentication/login"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
import phonenumbers

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
