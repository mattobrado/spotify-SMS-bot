"""Seed file to make sample data for spotify_group_chat db"""

from models import HostUser, Playlist, db
from app import app
from spotify import create_playlist

# Create all tables
db.drop_all()
db.create_all()