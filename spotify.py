from flask import redirect
import requests
from urllib.parse import urlencode

from mysecrets import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

API_BASE_URL = 'https://accounts.spotify.com/authorize?'
REDIRECT_URI = 'http://localhost:5000/'
SCOPE = 'user-read-private user-read-email'

def authorize():
  """Authorize the app to access a user's account"""
  auth_query_parameters = {
    "response_type": "code",
    "client_id": SPOTIFY_CLIENT_ID,
    "scope": SCOPE,
    "redirect_uri": REDIRECT_URI
    # "state": STATE
  }
  return f"{API_BASE_URL}{urlencode(auth_query_parameters)}"