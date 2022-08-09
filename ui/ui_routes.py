""" User interface """

from flask import Blueprint, flash, redirect, render_template, session

from .ui_forms import CreatePlaylistForm, PhoneForm
from models import GuestUser, HostUser, Playlist
from spotify import create_playlist
from app import db
from sms import MY_TWILIO_NUMBER, playlist_key_success_notification

ui = Blueprint("ui", __name__, template_folder="templates")


@ui.route('/')
def redirect_to_active_playlist():
  """Bring a user to their active playlist page"""

  host_user = get_host_user_from_session() # Get the host user object from id stored in session

  # Prevent users from jumping ahead to user interface without authorizing first
  if not host_user:
    return redirect('/auth')
  
  # If the user soes not have a phone number, rediect the the phone number form
  if not host_user.phone_number:
    return redirect('/user/phone')

  playlist_id = host_user.active_playlist_id # Get the users active playlist

  # If the user doesn't have an active playlist
  if not playlist_id:
    return redirect("/user/playlists") # Redirect the user to the playlists page to create a playlist
  
  return redirect(f"/user/{playlist_id}") # Redirect to the user's active playlist page


@ui.route('/phone', methods = ['GET', 'POST'])
def get_phone_number():
  """Get a user's phone number using the PhoneForm"""

  host_user = get_host_user_from_session() # Get the host user object from id stored in session

  # Prevent users from jumping ahead to user interface without authorizing first
  if not host_user:
    return redirect('/auth')
    
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


@ui.route('/<string:id>', methods=['GET', 'POST'])
def show_playlist(id):
  """Show a user's playlist"""
  
  host_user = get_host_user_from_session()

  # Prevent users from jumping ahead to /user without first authorizing
  if not host_user:
    return redirect('/auth')

  playlist = Playlist.query.filter_by(id = id).first() # Get the playlist

  if not playlist:
    return redirect("/user/playlists") # Redirect the user to the playlists page to create a playlist

  return render_template('view_playlist.html', host_user=host_user, playlist=playlist, twilio_phone_number = MY_TWILIO_NUMBER)

@ui.route('/<string:id>/delete', methods=['POST'])
def delete_playlist(id):
  """Delete a playlist"""

  playlist = Playlist.query.get_or_404(id) # Get the playlist

  # If the host user is the owner of the playlist
  if playlist.owner_id == session['host_user_id']:
    # Get users who have that playlist as their active playlist
    guest_users = GuestUser.query.filter_by(active_playlist_id=id).all()
    for guest_user in guest_users:
      guest_user.active_playlist_id = None # Set thier active playlist id to None
      db.session.add(guest_user)
    
    db.session.delete(playlist) # delete the playlist (This will not delete the playlist on spotify)
    db.session.commit()
    flash('Playlist Deleted', 'warning')
    return redirect('/user/playlists')
  
  # HostUser is not authorized to delete the playlist
  else:
    flash('You cannot delete that playlist')

  return redirect('/user')


@ui.route('/<string:id>/activate', methods=['POST'])
def activate_playlist(id):
  """Set a playlist to be a user's active playlist"""

  host_user = get_host_user_from_session()
  playlist = Playlist.query.get_or_404(id) # Get the playlist

  if playlist:
    host_user.active_playlist_id = playlist.id
    db.session.add(host_user) 
    db.session.commit()
    playlist_key_success_notification(phone_number=host_user.phone_number, playlist=playlist) # Send a message to the user
    flash('Playlist activated, Spotify links recieved from you will be added here', 'success')
    return redirect(f"/user/{playlist.id}")

  return redirect('/user')


@ui.route('/playlists', methods = ['GET', 'POST'])
def show_all_playlists():
  """Show all of users playlists and a """

  host_user = get_host_user_from_session()

  # Prevent users from jumping ahead without first authorizing
  if not host_user:
    return redirect('/auth')
  
  form = CreatePlaylistForm() # Form for making a new playlist

  # When the form is submitted
  if form.validate_on_submit():
    title = form.title.data # Get title from form
    key = form.key.data.lower()
    create_playlist(host_user=host_user, title=title, key=key) # Create the playlist
    flash('Playlist Created', 'success')
    return redirect('/user')

  return render_template('all_playlists.html', host_user=host_user, form=form)

def get_host_user_from_session():
  """Prevent users from jumping ahead to /user without first authorizing"""

  if 'host_user_id' not in session:
    return None

  return HostUser.query.filter_by(id=session['host_user_id']).first() # Get host_user using host_user_id in session

@ui.route('/tutorial', methods = ['GET', 'POST'])
def tutorial():
  """Show the tutuorial video"""
  host_user = get_host_user_from_session() # Get the host user object from id stored in session

  # Prevent users from jumping ahead to user interface without authorizing first
  if not host_user:
    return redirect('/auth')

  return render_template('tutorial.html', host_user=host_user)