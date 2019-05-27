import json, threading
from datetime import datetime

from sqlalchemy import desc
from flaskr.config import db, ma


class DldAgentModel(db.Model):
    __tablename__ = 'DldAgent'
    agent_id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer)
    thread_name = db.Column(db.String(32))
    status = db.Column(db.String(32))
    starttime = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DldAgentSchema(ma.ModelSchema):
    class Meta:
        model = DldAgentModel
        sqla_session = db.session


def add_new_agent(video_id, name, status):
    # Create a video instance using the schema and the passed in video
    agent = { "video_id": video_id, "thread_name": name, "status": status, "starttime": datetime.utcnow}
    schema = DldAgentSchema()
    new_agent = schema.load(agent, session=db.session).data

    # Add the person to the database
    db.session.add(new_agent)
    db.session.commit()

    # Serialize and return the newly agent
    data = schema.dump(new_agent).data
    return data

def get_agent_by_thread_name(name):
    agent = DldAgentModel.query.filter(DldAgentModel.thread_name == name).one_or_none()
    # did we find a video?
    if agent is not None:
        # serialize the data for the response
        schema = DldAgentSchema()
        data = schema.dump(agent).data
        return data

    return None

def get_agent_by_video_id(video_id):
    agent = DldAgentModel.query.filter(DldAgentModel.video_id == video_id).one_or_none()
    # did we find a video?
    if agent is not None:
        # serialize the data for the response
        schema = DldAgentSchema()
        data = schema.dump(agent).data
        return data

    return None

def delete_agent_by_thread_name(name):
    agent = DldAgentModel.query.filter(DldAgentModel.thread_name == name).one_or_none()
    
    if agent is not None:
        db.session.delete(agent)
        db.session.commit()

        # serialize the data for the response
        schema = DldAgentSchema()
        data = schema.dump(agent).data
        return data

    return None


