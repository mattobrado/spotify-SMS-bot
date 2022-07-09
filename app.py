from flask import Flask, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from spotifyGroupChatSecrets import SECRET_KEY
from models import Playlist, connect_db, db, User
from forms import UserForm, PlaylistForm
from sqlalchemy.exc import IntegrityError

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
  """Regiter new user"""
  form = UserForm()
  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    new_user = User.register(username=username, password=password)

    db.session.add(new_user)

    try:
      db.session.commit()
    except IntegrityError:
      form.username.errors.append('Username taken.')
      return render_template('users/signup.html', form=form)
    
    session['user_id'] = new_user.id
    flash('Welcome! Successfully create you account!', 'success')
    return redirect('/')

  return render_template('users/signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
  """Login for user"""
  form = UserForm()
  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    user = User.authenticate(username=username, password=password)
    
    if user:
      flash('Logged in', 'success')
      session['user_id'] = user.id
      return redirect('/playlists')
    else:
      form.username.errors = ['Invalid username/password']
  return render_template('users/login.html',form=form)

@app.route('/logout')
def logout_user():
  session.pop('user_id')
  return redirect('/')

@app.route('/playlists', methods=['GET', 'POST'])
def show_playlists():
  """Show list of playlists"""
  if 'user_id' not in session:
    flash('Please log in', 'warning')
    return redirect('/')
  form = PlaylistForm()
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
  flash('You cannot delete that playlist')

  return redirect('/playlists')