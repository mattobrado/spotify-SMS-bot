from unittest import TestCase
from app import app
from flask import session

class UITests(TestCase):

  def setUp(self):
    """Before every test"""

    self.client = app.test_client()
    app.config['TESTING'] = True