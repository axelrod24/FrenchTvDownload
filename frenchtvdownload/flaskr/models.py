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


class VideoModel(db.Model):
    __tablename__ = 'video'
    video_id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), index=True)
    status = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # mdata = db.Column(db.JSON)
    mdata = db.Column(db.String(4096))

    def get_video_by_id(self, video_id):
        video = self.query.filter(VideoModel.video_id == video_id).one_or_none()
        return video


class VideoSchema(ma.ModelSchema):
    class Meta:
        model = VideoModel
        sqla_session = db.session



