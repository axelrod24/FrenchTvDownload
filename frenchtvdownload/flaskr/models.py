from datetime import datetime
from flaskr.config import db, ma

class Person(db.Model):
    __tablename__ = 'person'
    person_id = db.Column(db.Integer, primary_key=True)
    lname = db.Column(db.String(32), index=True)
    fname = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PersonSchema(ma.ModelSchema):
    class Meta:
        model = Person
        sqla_session = db.session

class Video(db.Model):
    __tablename__ = 'video'
    video_id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), index=True)
    status = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VideoSchema(ma.ModelSchema):
    class Meta:
        model = Video
        sqla_session = db.session

        