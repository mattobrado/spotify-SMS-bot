"""Spotify GroupChat app"""

from urllib import response
from flask import Flask, redirect, render_template, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from twilio.twiml.messaging_response import MessagingResponse

from my_secrets import SECRET_KEY
from models import Playlist, connect_db, db, User
from forms import PhoneForm, PlaylistForm
from spotify import AUTHORIZATION_URL, create_playlist, get_access_token_header, get_profile_data


app = Flask(__name__) # Create Flask object

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spotify_group_chat' # PSQL database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Don't track modifications
app.config['SECRET_KEY'] = SECRET_KEY # SECRET_KEY for debug toolbar
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False # Disable intercepting redirects

toolbar = DebugToolbarExtension(app) # Create debug toolbar object
bootsrap =Bootstrap(app)

connect_db(app) # Connect database to Flask object 
db.create_all() # Create all tables


@app.route('/')
def root():
  """Redirect to /authorize"""
  return redirect('/authorize')

# -------------------------- AUTHORIZATION/LOGIN ---------------------------

@app.route('/authorize', methods=['GET', 'POST'])
def get_authorization():
  """1st call in the Spotify authorization process.
  
  Request authorization to access data"""

  return redirect(AUTHORIZATION_URL) # AUTHORIZATION_URL is assembled in spotify.py


@app.route('/login')
def login():
  """2nd call in the Spotify authorization process.
  
  Request access token"""

  code = request.args['code'] # Get code returned from authorization
  access_header = get_access_token_header(code) # Get a header to add to future requests
  session['access_header'] = access_header # Store access header in session

  profile_data = get_profile_data(access_header) # Make an API request to get profile data

  display_name = profile_data['display_name']
  email = profile_data['email']
  url = profile_data['external_urls']['spotify']
  id = profile_data['id']

  user = User.query.filter_by(email=email).first() # Look up user

  # If the user is not in the database
  if not user:
    user = User(display_name=display_name, email=email, url=url, id=id) # Create User object
    db.session.add(user) # Add User
    db.session.commit()
    flash('New Account Created!', 'success')

  else:
    flash(f"Welcome back {user.display_name}!", 'success')
  
  session['user_id'] = user.id # Save user_id in session

  return redirect('/profile')


@app.route('/switch-user')
def switch_user():
  """Remove user id and redirect to the authorization route"""

  session.pop('user_id') # Remover user_id from session
  return redirect('/authorize')


# -------------------------- PROFILE PAGE ---------------------------

@app.route('/phone', methods = ['GET', 'POST'])
def get_phone_number():
  
  user = User.query.get_or_404(session['user_id'])
  form = PhoneForm() # Form for getting phone numbers

  if form.validate_on_submit():
    phone_number = form.phone.data
    print(phone_number)
    user.phone_number = phone_number

    db.session.add(user)
    db.session.commit()
    flash('Phone Number Updated', 'success')
    return redirect('/profile')
  
  return render_template('phone.html', user=user, form=form)


@app.route('/profile', methods=['GET', 'POST'])
def show_profile():
  """Show a user's profile and a list of their SMS playlists"""
  
  if 'user_id' not in session:
    flash('Please log in', 'warning')
    return redirect('/authorize')
  
  user = User.query.get_or_404(session['user_id']) # Get user using user_id in session
  
  if not user.phone_number :
    flash('Enter your phone number to create a playlist', 'warning')
    return redirect('/phone')
  
  form = PlaylistForm() # Form for making a new playlist

  if form.validate_on_submit():
    title = form.title.data
    user_id = session['user_id']
    url = create_playlist(access_header=session['access_header'], user_id=user_id, title=title)
    new_playlist = Playlist(title=title, user_id=user_id, url=url)
    db.session.add(new_playlist)
    db.session.commit()
    flash('Playlist Created', 'success')
    return redirect('/profile')

  return render_template('profile.html', user=user, form=form)


@app.route('/profile/<int:playlist_id>/delete', methods=['POST'])
def delete_playlist(playlist_id):
  """Delete a playlists"""

  playlist = Playlist.query.get_or_404(playlist_id)
  if playlist.user_id == session['user_id']:
    db.session.delete(playlist)
    db.session.commit()
    flash('Playlist Deleted', 'warning')
    return redirect('/profile')
  
  # User was not authorized to delete that playlist
  else:
    flash('You cannot delete that playlist')

  return redirect('/profile')


@app.route('/api/receive_sms', methods=['POST'])
def receive_sms():
  """Route for Twilio to pass in recieved messages"""
  
  number = request.form['From']
  body = request.form['Body']
  
  print("***************************************")
  print(number)
  print(body)
  
  
  resp = MessagingResponse ()
  resp.message('Song added!')

  print(resp)
  print(str(resp))
  dir(resp)
  
  return str(resp)