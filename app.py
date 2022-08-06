"""Spotify GroupChat app"""

from flask import Flask, redirect
# from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap5
import os

# from my_secrets import SECRET_KEY
from models import connect_db, db
from demo.demo_routes import demo
from auth.auth_routes import auth
from ui.ui_routes import ui
from api.api_routes import api

app = Flask(__name__) # Create Flask object
app.register_blueprint(demo, url_prefix="/demo")
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(ui, url_prefix="/user")
app.register_blueprint(api, url_prefix="/api")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgres:///spotify_sms_playlist').replace("://", "ql://", 1) # PSQL database

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Don't track modifications
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'calebshouse') # SECRET_KEY for debug toolbar
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False # Disable intercepting redirects

# toolbar = DebugToolbarExtension(app) # Create debug toolbar object
bootsrap =Bootstrap5(app) # Create bootstrap object

connect_db(app) # Connect database to Flask object 
db.create_all() # Create all tables


@app.route('/')
def root():
  """Redirect to auth /auth"""

  return redirect('/auth')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return redirect('/')