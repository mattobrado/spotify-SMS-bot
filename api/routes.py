""" API for receiving text messages """

from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse

from models import Playlist
from spotify import add_tracks_to_playlist, get_or_create_guest_user, get_playlist_key_from_message, get_track_ids_from_message
from sms import ask_for_playlist_key, invalid_playlist_key_notification, playlist_key_success_notification
from app import db

api = Blueprint("api", __name__)

@api.route('/receive_sms', methods=['POST'])
def receive_sms():
  """Route for Twilio to pass in recieved messages"""

  phone_number = request.form['From']
  message = request.form['Body']
  
  track_ids = get_track_ids_from_message(message) # Scan message for track_ids
  playlist_key = get_playlist_key_from_message(message) # Scan message for playlist keys

  # If the message contained either a playlist key or track id
  if playlist_key or track_ids:
    guest_user = get_or_create_guest_user(phone_number=phone_number) # Get the guest user object

    # If the message contined a playlist key
    if playlist_key:
      playlist = Playlist.query.filter_by(key=playlist_key).first() # Get phone number's first playlist
      
      # If the key belongs to a playlist
      if playlist:
        guest_user.active_playlist_id = playlist.id # Set the guest user's active playlist to that playlist
        db.session.add(guest_user)
        db.session.commit()
        playlist_key_success_notification(phone_number=phone_number, playlist=playlist) # Send a message to the user
      else:
        invalid_playlist_key_notification(phone_number, playlist_key)

    # If the message contained track ids
    if track_ids:
      # If the guest user has an active playlist
      if guest_user.active_playlist_id:
        playlist = Playlist.query.filter_by(id=guest_user.active_playlist_id).first() # Get phone number's first playlist
        # If playlist in valid
        if playlist:
          add_tracks_to_playlist(playlist=playlist, track_ids=track_ids, added_by=phone_number) # Add the tracks to the playlist
      else:
        ask_for_playlist_key(phone_number) # Ask the guest user for a playlist key
    
  return str(MessagingResponse())