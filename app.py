"""Spotify GroupChat app"""

from flask import Flask, redirect, render_template, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from mysecrets import SECRET_KEY
from sqlalchemy.exc import IntegrityError

from models import Playlist, connect_db, db, User
from forms import UserForm, PlaylistForm
from spotify import AUTHORIZATION_URL, get_access_and_refresh_tokens, get_profile_data

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
  """Show homepage"""
  return render_template('homepage.html')


@app.route('/login', methods=['GET', 'POST'])
def login_user():
  """1st call in the Spotify Authetication process
  
  REQUEST AUTHORIZATION TO ACCESS DATA
  """

  # form = UserForm() # Form for getting username and password
  
  # if form.validate_on_submit():
  #   username = form.username.data.lower() # make username all lowercase
  #   password = form.password.data
  #   user = User.authenticate(username=username, password=password) # Get User object
    
  #   # If User.autheticate() returned a User object
  #   if user:
  #     flash('Logged in', 'success')
  #     session['user_id'] = user.id # add user's id'to session
  #     return redirect('/playlists')

  #   else:
  #     form.username.errors = ['Invalid username/password']

  # return render_template('users/login.html',form=form) # Reload login form

  return redirect(AUTHORIZATION_URL)


@app.route('/callback')
def callback():
  """REQUEST ACCESS AND REFRESH TOKENS"""

  auth_token = request.args['code']
  auth_header = get_access_and_refresh_tokens(auth_token)
  session['auth_header'] = auth_header

  profile_data = get_profile_data(auth_header) 

  display_name = profile_data['display_name']
  email = profile_data['email']
  profile_url = profile_data['external_urls']['spotify']

  user = User.query.filter_by(email=email).first()

  if not user:
    new_user = User(display_name=display_name, email=email, profile_url=profile_url) # Create User object
    db.session.add(new_user) # Add User
    db.session.commit()
  
  session['user_id'] = user.id

  return redirect('/profile')


@app.route('/profile')
def show_profile():
  """Show a user's profile"""

  user = User.query.get_or_404(session['user_id'])
  return render_template('profile.html', user=user)


@app.route('/signup', methods=['Get', 'POST'])
def signup_user():
  """Regiter new user, displays form and handles submission"""

  form = UserForm() # Form for getting username and password

  if form.validate_on_submit():
    username = form.username.data.lower() # make username all lowercase
    password = form.password.data

    new_user = User.register(username=username, password=password) # Create User object

    db.session.add(new_user) # Add User

    # Catch when a username already exists in the database
    try:
      db.session.commit()
    except IntegrityError:
      form.username.errors.append('Username taken.') # Show an error on the form
      return render_template('users/signup.html', form=form) # Reload form
    
    session['user_id'] = new_user.id #store user's id in session for authorization
    flash('Welcome! Successfully create you account!', 'success')
    return redirect('/')

  else:
    return render_template('users/signup.html', form=form)


@app.route('/logout')
def logout_user():
  """Logout route"""

  session.pop('user_id') # Remover user_id from session
  return redirect('/login')


@app.route('/playlists', methods=['GET', 'POST'])
def show_playlists():
  """Show list of playlists"""

  if 'user_id' not in session:
    flash('Please log in', 'warning')
    return redirect('/')

  form = PlaylistForm() # Form for making a new playlist
  all_playlists = Playlist.query.all()

  if form.validate_on_submit():
    title = form.title.data
    new_playlist = Playlist(title=title, user_id=session['user_id'])
    db.session.add(new_playlist)
    db.session.commit()
    flash('Playlist Created', 'success')
    return redirect('/playlists')
  
  return render_template('playlists.html', form=form, playlists=all_playlists)


@app.route('/playlists/<int:id>/delete', methods=['POST'])
def delete_playlist(id):
  """Delete a playlists"""

  playlist = Playlist.query.get_or_404(id)
  if playlist.user_id == session['user_id']:
    db.session.delete(playlist)
    db.session.commit()
    flash('Playlist deleted')
    return redirect('/playlists')
  
  # User was not authorized to delete that playlist
  else:
    flash('You cannot delete that playlist')

  return redirect('/playlists')

