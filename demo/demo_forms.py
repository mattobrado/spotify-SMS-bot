"""Forms for 'demo' blueprint"""

from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms.validators import DataRequired, Email

class EmailForm(FlaskForm):
  """Form to get email"""

  email = EmailField('Spotify Email Address', validators=[DataRequired(),Email()])