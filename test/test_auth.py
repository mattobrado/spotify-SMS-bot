from unittest import TestCase
from app import app
from flask import session

class AuthTests(TestCase):

  def setUp(self):
    """Before every test"""

    self.client = app.test_client()
    app.config['TESTING'] = True

  def test_auth(self):
    """Verify (/auth) redirects to spotify's authentication page"""
    
    with self.client:
      response = self.client.get('/auth/')

      self.assertEqual(response.status_code, 302)
      self.assertEqual(response.location, 'https://accounts.spotify.com/authorize/?response_type=code&client_id=8ef7a04961aa4c45b0ff10b1357ae880&scope=user-read-email+playlist-modify-public+playlist-modify-private&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fauth%2Flogin&show_dialog=True')

  def test_login(self):
    """Verify redirect from spitify is handled correctly"""

    with self.client:
      response = self.client.get('/auth/login/')