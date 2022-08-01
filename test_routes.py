from unittest import TestCase
from app import app
from flask import session

class FlaskTests(TestCase):

  def setUp(self):
    """Before every test"""

    self.client = app.test_client()
    app.config['TESTING'] = True

  def test_root(self):
    """Verify root (/) redirects to /authorize"""
    
    with self.client:
      response = self.client.get('/')

      self.assertEqual(response.status_code, 302)
      self.assertEqual(response.location, '/authorize')