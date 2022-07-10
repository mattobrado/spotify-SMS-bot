"""Spotify GroupChat app"""

from flask import Flask, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from mysecrets import SECRET_KEY
from sqlalchemy.exc import IntegrityError

from models import Playlist, connect_db, db, User
from forms import UserForm, PlaylistForm

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


@app.route('/login', methods=['GET', 'POST'])
def login_user():
  """Get login form and handle input"""

  form = UserForm() # Form for getting username and password
  
  if form.validate_on_submit():
    username = form.username.data.lower() # make username all lowercase
    password = form.password.data
    user = User.authenticate(username=username, password=password) # Get User object
    
    # If User.autheticate() returned a User object
    if user:
      flash('Logged in', 'success')
      session['user_id'] = user.id # add user's id'to session
      return redirect('/playlists')

    else:
      form.username.errors = ['Invalid username/password']

  return render_template('users/login.html',form=form) # Reload login form


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

@app.route('/user')
def user_page():
  """Show a user's profile"""

  return 'User page'