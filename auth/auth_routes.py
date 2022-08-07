""" authorization/login """

from flask import Blueprint, redirect, request, session
from spotify import AUTHORIZATION_URL, get_auth_tokens, get_or_create_host_user

auth = Blueprint("auth", __name__, template_folder="templates")


@auth.route('/', methods=['GET', 'POST'])
def get_authorization():
  """Make a call to the Spotify to request authorization to access a user's account"""
  # session.clear() # Remover user data from session
  
  return redirect(AUTHORIZATION_URL) # AUTHORIZATION_URL is assembled in spotify.py


@auth.route('/login')
def login():
  """Use code from spotify redirect to get authorizion and retrive or ceate a HostUser"""

  code = request.args['code'] # Get code returned from authorization
  auth_data = get_auth_tokens(code) # Get authorization header
  host_user = get_or_create_host_user(auth_data) # Get or create a HostUser based on their spotify profile data
  
  # if authentication was not successful
  print(f"host_user {host_user}")
  if not host_user:
    return redirect('/demo') # redirect to demo page

  session.clear() # Remove previous user data from session
  session['host_user_id'] = host_user.id # Save host_user_id in session
  return redirect('/user')