from unittest import TestCase
from app import app
from flask import session

class AuthTests(TestCase):

  def setUp(self):
    """Before every test"""

    self.client = app.test_client()
    app.config['TESTING'] = True

  def test_auth(self):
    """Verify /auth redirects to spotify's authentication page"""
    
    with self.client:
      response = self.client.get('/auth/')

      self.assertEqual(response.status_code, 302)
      self.assertEqual(response.location, 'https://accounts.spotify.com/authorize/?response_type=code&client_id=8ef7a04961aa4c45b0ff10b1357ae880&scope=user-read-email+playlist-modify-public+playlist-modify-private&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fauth%2Flogin&show_dialog=True')

  def test_login_user_without_access(self):
    """Verify redirect from Spotify is handled correctly when user is not added to the access list"""

    with self.client:
      # Fake redirect from spotify for an account without access
      response = self.client.get('/auth/login?code=AQAb_vZ6h6z7NTldkjT706Sjv3t5Is4a8j2rsSuIQ5zO2acUhIbDKZi4Yp4cYEUd1QG_3auWW8ytfCGxu6tRo3c8XLWhboGoib39_gmJQdzadnO099OhzF4kWazGWFtYS0OxxohLxyilA2PhYVVDDV2iazI52zf4BSiglyj4i9vPU4TzCSTRQAfHdA5vgXgdmXY0lNV7OhoB9mbIGqwNhmZYv_jzqXIN9GlhW1CRPAq6il1AVWHhf6eoJfNgybSox1mz9YAo')

      self.assertEqual(response.status_code, 302)
      self.assertEqual(response.location, '/demo')

  def test_logout(self):
    """Verify redirect from Spotify is handled correctly when user is not added to the access list"""

    with self.client as client:
      with client.session_transaction() as sess:
        sess['host_user_id'] = 'testuser' # add a user to the session

      response = self.client.get('/auth/logout')

      self.assertIsNone(session.get('host_user_id'))
      self.assertEqual(response.status_code, 302)
      self.assertEqual(response.location, '/auth')