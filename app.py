from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
from spotifyGroupChatSecrets import SECRET_KEY
from models import connect_db, db

app = Flask(__name__) # Create Flask object
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///spotify_group_chat" # PSQL database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Don't track modifications
app.config['SECRET_KEY'] = SECRET_KEY # SECRET_KEY for debug toolbar


app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False # Disable intercepting redirects

toolbar = DebugToolbarExtension(app) # Create debug toolbar object

connect_db(app) # Connect database to Flask object 
db.create_all() # Create all tables

@app.route('/')
def root():
  """Show homepage"""
  return render_template("homepage.html")