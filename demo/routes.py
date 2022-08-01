from flask import Blueprint, redirect, render_template
from .forms import EmailForm
from sms import send_request_access_message

demo = Blueprint("demo", __name__, static_folder="static", template_folder="templates")

@demo.route("/", methods=['GET', 'POST'])
def show_demo():
  """Show demo video and ask fro email"""

  form = EmailForm()

  if form.validate_on_submit():
    send_request_access_message(form.email.data)
    return redirect('/demo/thanks')
  return render_template('demo.html',form=form)

@demo.route('/thanks', methods=['GET', 'POST'])
def thanks():
  """"""

  return render_template('thanks.html')