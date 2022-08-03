from unittest import TestCase
from app import app
from flask import session

class DemoTests(TestCase):

  def setUp(self):
    """Before every test"""

    self.client = app.test_client()
    app.config['TESTING'] = True

  def test_demo_page(self):
    """Test demo page show instructions"""

    with self.client:
      response = self.client.get('/demo/')

    self.assertEqual(response.status_code, 200)
    self.assertIn(b'users must be explicitly added', response.data)

  def test_thanks_page(self):
    """Test demo page show instructions"""

    with self.client:
      response = self.client.get('/demo/thanks')

    self.assertEqual(response.status_code, 200)
    self.assertIn(b'Thanks', response.data)