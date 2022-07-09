from flask import Flask, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from spotifyGroupChatSecrets import SECRET_KEY
from models import connect_db, db, User
from forms import UserForm

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

@app.route('/register', methods=["Get", "POST"])
def register_user():
  form = UserForm()
  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    new_user = User.register(username=username, password=password)

    db.session.add(new_user)
    db.session.commit()
    flash("Welcome! Successfully create you account!")
    return redirect('/')

  return render_template("register.html", form=form)