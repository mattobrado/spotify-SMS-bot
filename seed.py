"""Seed file to make sample data for spotify_group_chat db"""

from models import HostUser, Playlist, db
from app import app
from spotify import create_playlist

# Create all tables
db.drop_all()
db.create_all()

# Add users
# bobeode = HostUser(display_name="bobeode",email="bobeode@gmail.com",url="fakeurl.com")
# wolfgang = HostUser(display_name="wolfgang",email="wolfgang@gmail.com",url="fakeurl.com")
# yikem = HostUser(display_name="yikem",email="yikem@gmail.com",url="fakeurl.com")
djobrad = HostUser(display_name="djobrad",email="mcobradovic@yahoo.com",url="https://open.spotify.com/user/1245079776", id=1245079776)

# db.session.add(bobeode)
# db.session.add(wolfgang)
# db.session.add(yikem)
db.session.add(djobrad)
db.session.commit()

# Add playlists
seed_playlist = Playlist(id='50dsaJ615KCP3WTRBd5e2v', title='Seed Playlist', key='key', url='https://open.spotify.com/playlist/50dsaJ615KCP3WTRBd5e2v', endpoint='https://api.spotify.com/v1/playlists/50dsaJ615KCP3WTRBd5e2v', owner_id='1245079776')

db.session.add(seed_playlist)
db.session.commit()

# # Add songs
# happy_birthday = Track(title="Happy Birthday", artist="Party People")
# fantazia = Track(title="FANTAZIA", artist="Roy Blair")
# bad_habit = Track(title="Bad Habit", artist="Steve Lacy")

# db.session.add(happy_birthday)
# db.session.add(fantazia)
# db.session.add(bad_habit)
# db.session.commit()
