"""Seed file to make sample data for spotify_group_chat db"""

from models import db
# Create all tables

db.drop_all()
db.create_all()