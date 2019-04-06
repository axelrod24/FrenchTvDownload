import json
from datetime import datetime
from flaskr.config import db, ma


class VideoModel(db.Model):
    __tablename__ = 'video'
    video_id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), index=True)
    status = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # mdata = db.Column(db.JSON)
    mdata = db.Column(db.String(4096))

class VideoSchema(ma.ModelSchema):
    class Meta:
        model = VideoModel
        sqla_session = db.session


def get_video_by_id(video_id):
    video = VideoModel.query.filter(VideoModel.video_id == video_id).one_or_none()
    # did we find a video?
    if video is not None:
        # serialize the data for the response
        schema = VideoSchema()
        data = schema.dump(video).data
        return data

    return None


def get_video_by_status(status):
    video = VideoModel.query.filter(VideoModel.status == status).one_or_none()
    # did we find a video?
    if video is not None:
        # serialize the data for the response
        schema = VideoSchema()
        data = schema.dump(video).data
        return data

    return None


def get_video_by_url(video_url):
    video = VideoModel.query.filter(VideoModel.url == video_url).one_or_none()
    # did we find a video?
    if video is not None:
        # serialize the data for the response
        schema = VideoSchema()
        data = schema.dump(video).data
        return data

    return None

def delete_video_by_id(video_id):
    video = VideoModel.query.filter(VideoModel.video_id == video_id).one_or_none()
    if video is not None:
        # delete the video from the database 
        db.session.delete(video)
        db.session.commit()

        # return video data
        schema = VideoSchema()
        data = schema.dump(video).data
        return data

    return None    


def get_all_video():
    video = VideoModel.query.order_by(VideoModel.timestamp).all()
    # Serialize the data for the response
    schema = VideoSchema(many=True)
    data = schema.dump(video).data    
    return data


def add_new_video(url, status, mdata):
    # Create a video instance using the schema and the passed in video
    video = { "url": url, "status": status, "mdata": mdata }
    schema = VideoSchema()
    new_video = schema.load(video, session=db.session).data

    # Add the person to the database
    db.session.add(new_video)
    db.session.commit()

    # Serialize and return the newly created person in the response
    data = schema.dump(new_video).data
    return data


def update_video_by_id(video_id, status, url=None, mdata=None):
    video = VideoModel.query.filter(VideoModel.video_id == video_id).one_or_none()
    if video is not None:
        video.status = status

        if mdata is not None:
            if isinstance(mdata, dict):
                video.mdata = json.dumps(mdata)
            else: 
                video.mdata = mdata

        if url is not None:
            video.url = url

        db.session.merge(video)
        db.session.commit()
         # Serialize and return the newly created person in the response
        schema = VideoSchema()
        data = schema.dump(video).data
        return data
        
    return None


def clean_model_at_startup():
    pass
