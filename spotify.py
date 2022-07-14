import base64
import json
import requests
import re
from urllib.parse import urlencode

from my_secrets import SPOTIFY_CLIENT_SECRET
from models import Playlist, db

SPOTIFY_AUTH_BASE_URL = 'https://accounts.spotify.com'
SPOTIFY_AUTH_URL= SPOTIFY_AUTH_BASE_URL + '/authorize'
SPOTIFY_TOKEN_URL = SPOTIFY_AUTH_BASE_URL + '/api/token'

SPOTIFY_API_URL = 'https://api.spotify.com/v1'
USER_PROFILE_ENDPOINT = SPOTIFY_API_URL + '/me'

SPOTIFY_CLIENT_ID = '8ef7a04961aa4c45b0ff10b1357ae880'
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
def get_auth_token_header(code):
  """2nd call in the Spotify Authetication process

  Pass the authorization code returned by the first call and the client 
  secret key to the Spotify Accounts Service '/api/token' endpoint. 
  
  Returns an access token and also a refresh token.
  """
  # Encode client id and secret key
  client_info_base64encoded = base64.b64encode((f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}").encode()) 
  headers = {"Authorization": f"Basic {client_info_base64encoded.decode()}"}

  data = {
      "code": str(code),
      "redirect_uri": REDIRECT_URI,
      "grant_type": "authorization_code"
  }

  # Pass the authorization code and the client s ecret key to the Spotify Accounts Service
  auth_request = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)

  # Tokens returned 
  response_data = json.loads(auth_request.text)
  access_token = response_data["access_token"]

  # Store access token to access Spotify API
  auth_header = json.dumps({"Authorization": f"Bearer {access_token}"}) # json.dumps() so we can store the string in our database
  return auth_header


# -------------------------- OTHER REQUESTS ---------------------------
def get_profile_data(auth_header):
  """Make a request to the spotify API and return profile data"""

  resp = requests.get(USER_PROFILE_ENDPOINT, headers=auth_header)
  return resp.json() # Use .json() to convert to a python Dict


def create_playlist(auth_header, user_id, title):
  """Create a playlist on the users account"""

  # Data for created playlist
  data = json.dumps({
    "name": title,
    "description": "Spotify SMS Playlist",
    "public": False, # Collaborative playlists cannot be public
    "collaborative": True 
  })

  create_playlist_endpoint = SPOTIFY_API_URL + f"/users/{user_id}/playlists"

  playlist_response= requests.post(create_playlist_endpoint, headers=auth_header, data=data)
  playlist_data = json.loads(playlist_response.text) # Unpack response
  
  id = playlist_data['id'] # Use the same id as spotify
  url = playlist_data['external_urls']['spotify'] # Used for links in user interface
  playlist_endpoint = playlist_data['href'] # Used for adding tracks
  owner_id = playlist_data['owner']['id'] # Use the same owner id as spotify

  new_playlist = Playlist(id=id, title=title, url=url, endpoint=playlist_endpoint, owner_id=owner_id)
  db.session.add(new_playlist)
  db.session.commit() # commit to database
  
  return new_playlist


def get_track_ids_from_message(message):
  """Returns a list of Spotify track URLs in a string"""

  track_ids = [] # List of track_ids to return

  urls = re.findall('https:\/\/open.spotify.com\/track\/+[^? ]*', message) # Regex for finding track urls
  
  # Iterate over found urls
  for url in urls:
    track_id = url.replace('https://open.spotify.com/track/', '') # replace the begining to get the track id
    track_ids.append(track_id) # Append track_id to our list to return

  return track_ids


def add_tracks_to_playlist(playlist, track_ids):
  """Make a post request to add the track_ids to the Spotify playlist"""

  auth_header = playlist.owner.auth_header # get auth_header of the playlist's owner
  add_tracks_endpoint = playlist.endpoint + "/tracks"
  
  # Pass the track_ids to spotify in the query string with the key "uris"
  uris_string = 'spotify:track:' + track_ids[0] # Format the first track track_ids[0]

  # For all track_ids after the first (track_ids[1:]) add them with a comma seperator
  for track_id in track_ids[1:]:
    uris_string = uris_string + ',' + 'spotify:track:' + track_id

  # Make the post request to add the tracks to the playlist
  request = requests.post(add_tracks_endpoint, headers=auth_header, params={"uris": uris_string})
  # print(request.text)