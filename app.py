from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
from spotifyGroupChatSecrets import SECRET_KEY

app = Flask(__name__) # Create Flask object
app.config['SECRET_KEY'] = SECRET_KEY # SECRET_KEY for debug toolbar

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False # Disable intercepting redirects

toolbar = DebugToolbarExtension(app) # Create debug toolbar object

@app.route('/')
def root():
  """Show homepage"""
  return render_template("index.html")