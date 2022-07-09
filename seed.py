"""Seed file to make sample data for spotify_group_chat db"""

from models import User, Playlist, Song, db
from app import app

# Create all tables
db.drop_all()
db.create_all()

# Add users
bobeode = User.register(username="bobeode",password="password")
wolfgang = User.register(username="wolfgang",password="password")
yikem = User.register(username="yikem",password="password")

db.session.add(bobeode)
db.session.add(wolfgang)
db.session.add(yikem)
db.session.commit()

# Add playlists
road_trip = Playlist(title="Road Trip", user_id=1)
cooking = Playlist(title="Cooking", user_id=2)
party = Playlist(title="party", user_id=3)

db.session.add(road_trip)
db.session.add(cooking)
db.session.add(party)
db.session.commit()

# Add songs
happy_birthday = Song(title="Happy Birthday", artist="Party People")
fantazia = Song(title="FANTAZIA", artist="Roy Blair")
bad_habit = Song(title="Bad Habit", artist="Steve Lacy")

db.session.add(happy_birthday)
db.session.add(fantazia)
db.session.add(bad_habit)
db.session.commit()
