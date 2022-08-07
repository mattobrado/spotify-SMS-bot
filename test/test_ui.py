from unittest import TestCase

import phonenumbers
from app import app
from models import HostUser, db
from flask import session

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spotify_sms_playlist_test' # Test database
app.config['SQLALCHEMY_ECHO'] = False
app.config['WTF_CSRF_ENABLED'] = False # Don't req CSRF for testing
app.config['TESTING'] = True

db.drop_all()
db.create_all()

# Create a HostUser without a phone number
host_user = HostUser(id='1245079776', 
  display_name='djobrad', 
  email='mcobradovic@yahoo.com',
  url='https://open.spotify.com/user/1245079776')

db.session.add(host_user)
db.session.commit()

test_playlist_id = '6hKkMi8kOl44uM8AJUtw6s'
# 6hKkMi8kOl44uM8AJUtw6s | test playlist | test | https://open.spotify.com/playlist/6hKkMi8kOl44uM8AJUtw6s | https://api.spotify.com/v1/playlists/6hKkMi8kOl44uM8AJUtw6s | 1245079776

class UserNotInSessionTests(TestCase):

  def test_ui_user_not_in_session(self):
    """Test going to /user/ without being logged in"""

    self.client = app.test_client()
    response = self.client.get('/user/')

    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.location, '/auth')

  def test_phone_user_not_in_session(self):
    """Test going to /user/phone/ without being logged in"""

    self.client = app.test_client()
    response = self.client.get('/user/phone')

    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.location, '/auth')
  
  def test_playlist_user_not_in_session(self):
    """Test going to a playlist page without being logged in"""

    self.client = app.test_client()
    response = self.client.get(f"/user/{test_playlist_id}")

    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.location, '/auth')

  def test_all_playlists_user_not_in_session(self):
    """Test going to the all playlists page without being logged in"""

    self.client = app.test_client()
    response = self.client.get('/user/playlists')

    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.location, '/auth')

class UITests(TestCase):

  def setUp(self):
    """Before every test"""

    HostUser.query.delete()

    self.client = app.test_client()
    with self.client.session_transaction() as sess:
      sess['host_user_id'] = '1245079776'

  def tearDown(self):
    """Clean up test database"""

    db.session.rollback()

  def test_ui_user_without_phone_number(self):
    """Test going to /user/ without being logged in"""

    host_user.phone_number = None
    db.session.add(host_user)
    db.session.commit()

    response = self.client.get('/user/')

    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.location, '/user/phone')

  def test_ui_user_without_active_playlist(self):
    """Test user is redirected to all playlists page they have no active playlist"""

    host_user.phone_number = '+12345678'
    host_user.active_playlist_id = None
    db.session.add(host_user)
    db.session.commit()

    response = self.client.get('/user/')

    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.location, '/user/playlists')

  def test_ui_user_with_active_playlist(self):
    """Test user is redirected to thier active playlist page if they have one"""

    host_user.phone_number = '+12345678'
    host_user.active_playlist_id = test_playlist_id
    db.session.add(host_user)
    db.session.commit()

    response = self.client.get('/user/')

    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.location, f"/user/{test_playlist_id}")

