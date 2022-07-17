"""Functions to send messages to users"""

from twilio.rest import Client

from my_secrets import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, MY_TWILIO_NUMBER

account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

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
      body=f"Tell your friends to text #{playlist.key} to {MY_TWILIO_NUMBER} and songs recieved from them will be added to your playlist:{playlist.title}",
      from_= MY_TWILIO_NUMBER,
      to= phone_number
    )