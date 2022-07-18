"""Functions to send messages to users"""

import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
MY_TWILIO_NUMBER = os.environ.get('MY_TWILIO_NUMBER')
MY_PHONE_NUMBER = os.environ.get('MY_PHONE_NUMBER')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def ask_for_playlist_key(phone_number):
  """Send a message to a user asking for a playlist #key"""

  client.messages \
    .create(
      body="Which playlist do you want to add songs to? Ask the playlist's host for the #key.",
      from_= MY_TWILIO_NUMBER,
      to= phone_number
    )

def invalid_playlist_key_notification(phone_number, key):
  """Send a message to a user to notify them thier #key was invlaid"""

  client.messages \
    .create(
      body=f"Sorry, I couldn't find a playlist with a #key of #{key}",
      from_= MY_TWILIO_NUMBER,
      to= phone_number
    )

def playlist_key_success_notification(phone_number, playlist):
  """Send a message to a user to notify them thier #key was invlaid"""

  client.messages \
    .create(
      body=f"Success! Songs received from you will be added to #{playlist.key} {playlist.url}",
      from_= MY_TWILIO_NUMBER,
      to= phone_number
    )

def key_instructions_notification(phone_number, playlist):
  """Send a message to a user telling them how to add other people"""

  client.messages \
    .create(
      body=f"Tell your friends to text #{playlist.key} to {MY_TWILIO_NUMBER} and songs recieved from them will be added to your playlist",
      from_= MY_TWILIO_NUMBER,
      to= phone_number
    )

def send_request_access_message(email):
  """Send a message to a user telling them how to add other people"""

  client.messages \
    .create(
      body=f"{email} has requested access to spotify text message playlists",
      from_= MY_TWILIO_NUMBER,
      to= MY_PHONE_NUMBER
    )