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


class UserNotInSessionTests(TestCase):
  def test_ui_user_not_in_session(self):
    """Test going to /user/ without being logged in"""

    self.client = app.test_client()
    response = self.client.get('/user/')

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
    self.assertEqual(response.location, '/phone')

  def test_ui_user_without_active_playlist(self):
    """Test user is redirected to all playlists page they have no active playlist"""

    host_user.phone_number = '+12345678'
    db.session.add(host_user)
    db.session.commit()

    response = self.client.get('/user/')

    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.location, '/user/playlists')
