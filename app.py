"""Spotify GroupChat app"""

from flask import Flask, redirect, render_template, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from mysecrets import SECRET_KEY

from models import Playlist, connect_db, db, User
from forms import PlaylistForm
from spotify import AUTHORIZATION_URL, get_access_token_header, get_profile_data

app = Flask(__name__) # Create Flask object

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spotify_group_chat' # PSQL database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Don't track modifications
app.config['SECRET_KEY'] = SECRET_KEY # SECRET_KEY for debug toolbar
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False # Disable intercepting redirects

toolbar = DebugToolbarExtension(app) # Create debug toolbar object

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
  profile_url = profile_data['external_urls']['spotify']

  user = User.query.filter_by(email=email).first() # Look up user

  # If the user is not in the database
  if not user:
    user = User(display_name=display_name, email=email, profile_url=profile_url) # Create User object
    db.session.add(user) # Add User
    db.session.commit()
    flash('New Account Created!', 'success')

  else:
    flash(f"Welcome back {user.display_name}!", 'success')
  
  session['user_id'] = user.id # Save user_id in session

  return redirect('/profile')


@app.route('/switch-user')
def switch_user():
  """Remove user id and redirect to authorization route"""

  session.pop('user_id') # Remover user_id from session
  return redirect('/authorize')


# -------------------------- PROFILE PAGE ---------------------------

@app.route('/profile', methods=['GET', 'POST'])
def show_profile():
  """Show a user's profile and a list of their SMS playlists"""
  if 'user_id' not in session:
    flash('Please log in', 'warning')
    return redirect('/authorize')

  user = User.query.get_or_404(session['user_id']) # Get user using user_id in session
  form = PlaylistForm() # Form for making a new playlist

  if form.validate_on_submit():
    title = form.title.data
    new_playlist = Playlist(title=title, user_id=session['user_id'])
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

