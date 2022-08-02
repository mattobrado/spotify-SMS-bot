""" AUTHORIZATION/LOGIN """

from flask import Blueprint, flash, redirect, render_template, request, session
from spotify import AUTHORIZATION_URL, get_auth_tokens, get_or_create_host_user
from app import db
from .forms import PhoneForm
from models import GuestUser, HostUser

auth = Blueprint("auth", __name__, template_folder="templates")

@auth.route('/', methods=['GET', 'POST'])
def get_authorization():
  """Make a call to the Spotify to request authorization to access a user's account"""

  return redirect(AUTHORIZATION_URL) # AUTHORIZATION_URL is assembled in spotify.py


@auth.route('/login')
def login():
  """Use code from spotify redirect to get authorizion and retrive or ceate a HostUser"""

  code = request.args['code'] # Get code returned from authorization
  auth_data = get_auth_tokens(code) # Get authorization header
  host_user = get_or_create_host_user(auth_data) # Get or create a HostUser based on their spotify profile data
  
  # If we couldn't get user data we need to manulally
  if not host_user:
    return redirect('/demo')
  
  session['host_user_id'] = host_user.id # Save host_user_id in session
  return redirect('/user')


@auth.route('/log-out')
def log_out():
  """Remove host_user data from session and redirect to the authorization route"""

  session.clear() # Remover user data from session
  return redirect('/auth')


@auth.route('/phone', methods = ['GET', 'POST'])
def get_phone_number():
  """Get a user's phone number using the PhoneForm"""

  if 'host_user_id' not in session:
    return redirect('/auth')

  host_user = HostUser.query.get_or_404(session['host_user_id']) # Get host_user using host_user_id in session

  form = PhoneForm() # Form for getting phone numbers

  if form.validate_on_submit():
    guest_user = GuestUser.query.filter_by(phone_number=form.phone.data).first()
    # if there is a guest user with that phone number
    if guest_user:
      host_user.active_playlist_id = guest_user.active_playlist_id #copy the guest user's active playlist
      db.session.delete(guest_user) # delete guest user to replace them with host user
      db.session.commit()

    host_user.phone_number = form.phone.data # Set host user's phone number
    db.session.add(host_user)
    db.session.commit()
    flash('Phone Number Updated', 'success')
    return redirect('/user')
  
  return render_template('phone.html', user=host_user, form=form)