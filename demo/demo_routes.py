from flask import Blueprint, redirect, render_template
from .demo_forms import EmailForm
from sms import send_request_access_message

demo = Blueprint("demo", __name__, template_folder="templates")

@demo.route("/", methods=['GET', 'POST'])
def show_demo():
  """Show demo video and ask fro email"""

  form = EmailForm() # Form for getting an email address

  if form.validate_on_submit():
    send_request_access_message(form.email.data) # Send email address to myself to add it manually
    return redirect('/demo/thanks')

  return render_template('demo.html',form=form)

@demo.route('/thanks', methods=['GET', 'POST'])
def thanks():
  """"""

  return render_template('thanks.html')