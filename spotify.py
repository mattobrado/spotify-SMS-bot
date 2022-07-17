import json
import requests
import re
from urllib.parse import urlencode

from my_secrets import MY_TWILIO_NUMBER, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_HEADER 
from models import GuestUser, HostUser, Playlist, PlaylistTrack, Track, db
from sms import key_instructions_notification, playlist_key_success_notification

SPOTIFY_AUTH_BASE_URL = 'https://accounts.spotify.com'
SPOTIFY_AUTH_URL= SPOTIFY_AUTH_BASE_URL + '/authorize'
SPOTIFY_TOKEN_URL = SPOTIFY_AUTH_BASE_URL + '/api/token'

SPOTIFY_API_URL = 'https://api.spotify.com/v1'
USER_PROFILE_ENDPOINT = SPOTIFY_API_URL + '/me'

REDIRECT_URI = 'http://localhost:5000/login' 
SCOPE = 'user-read-email playlist-modify-public playlist-modify-private' # Scope of authorization

# ------------------------- REQUEST AUTHORIZATION TO ACCESS DATA ---------------------------
auth_query_parameters = {
  "response_type": "code",
  "client_id": SPOTIFY_CLIENT_ID,
  "scope": SCOPE,
  "redirect_uri": REDIRECT_URI,
  "show_dialog": True # This enables users to switch accounts
}

AUTHORIZATION_URL = f"{SPOTIFY_AUTH_URL}?{urlencode(auth_query_parameters)}"


# -------------------------- REQUEST ACCESS AND REFRESH TOKENS ----------------------------
def get_auth_tokens(code):
  """2nd call in the Spotify Authetication process

  Pass the authorization code returned by the first call and the client 
  secret key to the Spotify Accounts Service '/api/token' endpoint. 
  
  Returns the HTTP response as a python dictionary which contains the access_token and
  refresh_token
  """
  # Encode client id and secret key


  data = {
      "code": str(code),
      "redirect_uri": REDIRECT_URI,
      "grant_type": "authorization_code"
  }

  # Pass authorization code and client secret key to the Spotify Accounts Service
  auth_response = requests.post(SPOTIFY_TOKEN_URL, headers=SPOTIFY_CLIENT_HEADER , data=data)

  # Tokens returned 
  return json.loads(auth_response.text) #.json() to convert to a python dictionary


def refresh_access_token(user):
  """Get a new access token when the old access token is expired"""

  data = {
    "grant_type": "refresh_token",
    "refresh_token": user.refresh_token
  }

  auth_response = requests.post(SPOTIFY_TOKEN_URL, headers=SPOTIFY_CLIENT_HEADER, data=data)
  auth_data = json.loads(auth_response.text)

  user.access_token = auth_data["access_token"]

  db.session.add(user)
  db.session.commit()
  return user


def make_authorized_api_call(host_user, endpoint, method='POST', data=None, params=None):
  """Make an authorized api call with protection against expired access tokens.

  Return the responce in a python dictionary"""
  if method == 'POST':
    request_method = requests.post
  elif method == 'GET':
    request_method = requests.get

  request = request_method(endpoint, headers=host_user.auth_header, data=data,params=params)
  # Check for expired access token (error code 401)
  if request.status_code == 401:
    refresh_access_token(host_user) #refresh the owner's access_token
    request = request_method(endpoint, headers=host_user.auth_header, data=data,params=params) # make the request again
  # print(request.status_code)
  if request.status_code < 400:
    return json.loads(request.text) # Unpack response
  else:
    return None


# -------------------------- DATABASE ---------------------------

def get_or_create_host_user(auth_data):
  """Make a request to the spotify API and return a HostUser object"""

  access_token = auth_data["access_token"]
  refresh_token = auth_data["refresh_token"]

  auth_header = {"Authorization": f"Bearer {access_token}"}

  profile_data = requests.get(USER_PROFILE_ENDPOINT, headers=auth_header).json() # .json() to unpack

  # Get data from response
  display_name = profile_data['display_name']
  email = profile_data['email']
  url = profile_data['external_urls']['spotify']
  id = profile_data['id'] # Use same id as spotify

  host_user = HostUser.query.filter_by(email=email).first() # Check if the HostUser is already in the Database using email address

  # If the user is not in the database
  if not host_user:
    # Create HostUser object
    host_user = HostUser(display_name=display_name, email=email, url=url, id=id, access_token=access_token, refresh_token=refresh_token)
    db.session.add(host_user) # Add HostUser to Database
    db.session.commit() 

  # If the HostUser already exits update the access token and refresh token 
  else:
    host_user.access_token = access_token # Update access_token
    host_user.refresh_token = refresh_token # Update access_token
    db.session.add(host_user) # Update HostUser
    db.session.commit() 

  return host_user # return the HostUser object


def get_or_create_guest_user(phone_number):
  """Get or create a guest user object"""

  guest_user = GuestUser.query.filter_by(phone_number=phone_number).first() # Check if the HostUser is already in the Database using email address

  # If the user is not in the database
  if not guest_user:
    # Create HostUser object
    guest_user = GuestUser(phone_number=phone_number)
    db.session.add(guest_user) # Add HostUser to Database
    db.session.commit() 

  return guest_user # return the HostUser object


def create_playlist(host_user, title, key):
  """Create a playlist on the users account"""

  # Data for created playlist
  data = json.dumps({
    "name": title,
    "description": f"Text #{key} to {MY_TWILIO_NUMBER} to start adding songs via text",
    "public": False, # Collaborative playlists cannot be public
    "collaborative": True 
  })

  create_playlist_endpoint = SPOTIFY_API_URL + f"/users/{host_user.id}/playlists"

  playlist_data = make_authorized_api_call(host_user=host_user, endpoint=create_playlist_endpoint, data=data)

  id = playlist_data['id'] # Use the same id as spotify
  url = playlist_data['external_urls']['spotify'] # Used for links in user interface
  playlist_endpoint = playlist_data['href'] # Used for adding tracks
  owner_id = playlist_data['owner']['id'] # Use the same owner id as spotify

  new_playlist = Playlist(id=id, title=title, key=key, url=url, endpoint=playlist_endpoint, owner_id=owner_id)
  db.session.add(new_playlist)

  host_user.active_playlist_id = new_playlist.id
  db.session.add(host_user)
  db.session.commit() # commit to database

  playlist_key_success_notification(phone_number=host_user.phone_number, playlist=new_playlist) # Send a message to the user
  key_instructions_notification(phone_number=host_user.phone_number, playlist=new_playlist)

  return new_playlist


def get_or_create_track(host_user, track_id):
  """Make an API call to get rack data"""

  track = Track.query.filter_by(id=track_id).first() # Check if the Track is already in the Database
  
  if not track:
    get_track_endpoint = SPOTIFY_API_URL + '/tracks/' + track_id
    track_data = make_authorized_api_call(
      host_user=host_user, 
      method='GET', 
      endpoint=get_track_endpoint
    )
    # if the request was successful
    if track_data:

      id = track_data['id'] # Use same id as spotify
      name = track_data['name']
      artist = track_data['artists'][0]['name']
      track = Track(id=id, name=name, artist=artist)
      db.session.add(track)
      db.session.commit()
    
  return track

# -------------------------- OTHER REQUESTS ---------------------------

def get_track_ids_from_message(message):
  """Returns a list of Spotify track URLs in a string"""

  track_ids = [] # List of track_ids to return

  urls = re.findall('https:\/\/open.spotify.com\/track\/+[^? ]*', message) # Regex for finding track urls
  
  # Iterate over found urls
  for url in urls:
    track_id = url.replace('https://open.spotify.com/track/', '') # replace the begining to get the track id
    track_ids.append(track_id) # Append track_id to our list to return

  return track_ids


def get_playlist_key_from_message(message):
  """Returns the first playlist key in a message"""

  keys = re.findall('#+[^? ]*', message)  # find all words starting with "#"

  # if keys were found
  if keys:
    return keys[0].replace('#', '').lower() # return the first key in lowercase
  else:
    return None


def add_tracks_to_playlist(playlist, track_ids, added_by=None):
  """Make a post request to add the track_ids to the Spotify playlist"""

  add_tracks_endpoint = playlist.endpoint + "/tracks"
  
  # For all track_ids after the first (track_ids[1:]) add them with a comma seperator
  for track_id in track_ids:
    uris_string = 'spotify:track:' + track_id # Format the first track track_ids[0]

    # Make the post request to add the tracks to the playlist
    response = make_authorized_api_call(
      host_user=playlist.owner, 
      endpoint=add_tracks_endpoint, 
      params={"uris": uris_string}  # Pass the track_ids to spotify in the query string with the key "uris"
    )
    # If the request was successful
    if response:
      track = get_or_create_track(host_user=playlist.owner, track_id=track_id)
      new_playlist_track = PlaylistTrack(
        playlist_id=playlist.id, 
        track_id=track.id,
        added_by=added_by
      )
      db.session.add(new_playlist_track)
      db.session.commit()
      return new_playlist_track
  
  return None