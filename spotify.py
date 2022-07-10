import base64
import json
import requests
from urllib.parse import urlencode

from mysecrets import SPOTIFY_CLIENT_SECRET

SPOTIFY_AUTH_BASE_URL = 'https://accounts.spotify.com'
SPOTIFY_AUTH_URL= SPOTIFY_AUTH_BASE_URL + '/authorize'
SPOTIFY_TOKEN_URL = SPOTIFY_AUTH_BASE_URL + '/api/token'

SPOTIFY_CLIENT_ID = '8ef7a04961aa4c45b0ff10b1357ae880'
REDIRECT_URI = 'http://localhost:5000/callback' 
SCOPE = 'user-read-private user-read-email' # Scope of authorization

# -------------------------- REQUEST AUTHORIZATION TO ACCESS DATA ----------------------------
auth_query_parameters = {
  "response_type": "code",
  "client_id": SPOTIFY_CLIENT_ID,
  "scope": SCOPE,
  "redirect_uri": REDIRECT_URI
}

AUTHORIZATION_URL = f"{SPOTIFY_AUTH_URL}?{urlencode(auth_query_parameters)}"


# -------------------------- REQUEST ACCESS AND REFRESH TOKENS ----------------------------
def request_access_and_refresh_tokens(code):
  """The 2nd call in the Spotify Authetication process

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

  # Store access token to access Spotify API
  auth_header = {"Authorization": f"Bearer {access_token}"}
  return auth_header