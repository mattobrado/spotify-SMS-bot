"""Forms for demo Blueprint"""

from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms.validators import DataRequired, Email
import email_validator

class EmailForm(FlaskForm):
  """Form to get email"""
  email = EmailField('Spotify Email Address', validators=[DataRequired(),Email()])