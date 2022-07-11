import base64
import json
import requests
from urllib.parse import urlencode

from mysecrets import SPOTIFY_CLIENT_SECRET

SPOTIFY_AUTH_BASE_URL = 'https://accounts.spotify.com'
SPOTIFY_AUTH_URL= SPOTIFY_AUTH_BASE_URL + '/authorize'
SPOTIFY_TOKEN_URL = SPOTIFY_AUTH_BASE_URL + '/api/token'

SPOTIFY_API_URL = 'https://api.spotify.com/v1'
USER_PROFILE_ENDPOINT = SPOTIFY_API_URL + '/me'

SPOTIFY_CLIENT_ID = '8ef7a04961aa4c45b0ff10b1357ae880'
REDIRECT_URI = 'http://localhost:5000/login' 
SCOPE = 'user-read-private user-read-email' # Scope of authorization

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
def get_access_token_header(code):
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
  post_request = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)

  # Tokens returned 
  response_data = json.loads(post_request.text)
  access_token = response_data["access_token"]
  # raise
  # Store access token to access Spotify API
  auth_header = {"Authorization": f"Bearer {access_token}"}
  return auth_header


# -------------------------- DATA REQUESTS ---------------------------
def get_profile_data(auth_header):
  """Make a request to the spotify API and return profile data"""

  resp = requests.get(USER_PROFILE_ENDPOINT, headers=auth_header)
  return resp.json() # Use .json() to convert to a python Dict