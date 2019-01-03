
import os, threading

from frenchtvdownload.config import db, app
from config import db, app
from models import Video, VideoSchema
from flask import make_response, abort, jsonify

from dataclasses import dataclass
from typing import Any

from frtvdld.download import download_video
from frtvdld.DownloadException import *

class DldThread():
    def __init__(self, url, video_id):
        self.thread = threading.Thread(target=self.run)
        self.url = url
        self.video_id = video_id

        self.pipe_name = os.path.join(app.config["DLD_FOLDER"], app.config["PIPE_NAME_HEADER"] % self.thread.name)
        i=1
        while os.path.exists(self.pipe_name) is True:
            self.pipe_name = os.path.join(app.config["DLD_FOLDER"], (app.config["PIPE_NAME_HEADER"]+"_"+str(i)) % self.thread.name)
            i+=1

        os.mkfifo(self.pipe_name)
        print("video id:{video_id}, pipe name:{pipe_name}".format(video_id=self.video_id, pipe_name=self.pipe_name))

    def write_to_pipe(self, msg):
        pipeout = os.open(self.pipe_name, os.O_WRONLY)
        os.write(pipeout, msg)
        os.close(pipeout)

    def run(self):
        # loging progress to client thread        
        def p(x):
            # log to console
            print("Video id:%d - progress:%3d - %d/%d" % (self.video_id, min(int((x[0] * 100) / x[1]), 100), x[0], x[1]))
            # write to pipe for client update
            self.write_to_pipe(str.encode("%d\n" % (x[1]-x[0]+1)))

        try:
            download_video(self.url, base_folder=app.config["DLD_FOLDER"], progressFnct = p)

        except FrTvDownloadException as excepErr:
            if isinstance(excepErr, FrTvDwnVideoNotFound):
                error_msg = "Can't find video: %s" % self.url
            elif isinstance(excepErr, FrTvDwnPageParsingError):
                error_msg = "Can't get or parse video ID page: %s" % self.url
            elif isinstance(excepErr, FrTvDwnManifestUrlNotFoundError):
                error_msg = "Can't parse video metadata: %s" % self.url
            elif isinstance(excepErr, FrTvDwnMetaDataParsingError):
                error_msg = "Can't get manifest URL: %s" % self.url
            else:
                error_msg = "Unknown error getting metadata for %s" % self.url

            # logger.error(error)
            self.write_to_pipe(error_msg)


        # # write "done" to indicate end of download
        # pipeout = os.open(self.pipe_name, os.O_WRONLY)
        # os.write(pipeout, str.encode("done" ))
        # os.close(pipeout)
        
    def start(self):
        # start the thread and read from the pipe
        self.thread.start()
        self.pipein = open(self.pipe_name, 'r')

    def is_alive(self):
        return self.thread.is_alive() 

    def read_status(self):
        lines = self.pipein.readlines()
        print("line is:", lines)
        status = lines[-1:]
        return status

    def clean_up(self):
        # remove the pipe
        os.remove(self.pipe_name)


def read_all():
    """
    This function responds to a request for /api/video
    with the complete lists of video
    :return:        json string of list of video
    """
    # Create the list of people from our data
    video = Video.query.order_by(Video.timestamp).all()

    # Serialize the data for the response
    video_schema = VideoSchema(many=True)
    data = video_schema.dump(video).data
    return data

def addurl(url):
    print("url is : "+url)
    """
    This function creates a new person in the people structure
    based on the passed in person data
    :param person:  person to create in people structure
    :return:        201 on success, 406 on person exists
    """

    existing_url = (
        Video.query.filter(Video.url == url)
        .one_or_none()
    )

    # Can we insert this person?
    if existing_url is None:

        # Create a video instance using the schema and the passed in person
        schema = VideoSchema()
        video = { "url": url, "status":"pending"}
        new_video = schema.load(video, session=db.session).data

        # Add the person to the database
        db.session.add(new_video)
        db.session.commit()

        # Serialize and return the newly created person in the response
        data = schema.dump(new_video).data

        return data, 201

    # Otherwise, nope, person exists already
    else:
        abort(
            409,
            "Video {url} exists already".format(url=url),
        )

def download(video_id):
    """
    This function creates a new person in the people structure
    based on the passed in person data
    :param person:  person to create in people structure
    :return:        201 on success, 406 on person exists
    """

    # Get the video requested
    video = Video.query.filter(Video.video_id == video_id).one_or_none()

    # Did we find a video?
    if video is not None:

        video.status = "downloading"
        # merge the new object into the old and commit it to the db
        db.session.merge(video)
        db.session.commit()

        # create, store the thread and start it 
        dld_thread = DldThread(video.url, video.video_id)
        app.config["DLD_THREAD"][video.video_id] = dld_thread
        dld_thread.start() 

        # Serialize and return the newly created person in the response
        schema = VideoSchema()
        data = schema.dump(video).data

        return data, 201

    # Otherwise, nope, person exists already
    else:
        abort(
            409,
            "Can't find video {video_id}".format(video_id=video_id),
        )


def delete(video_id):
    """
    This function deletes a video meta data from db
    :param video_id:   Id of the video to delete
    :return:            200 on successful delete, 404 if not found
    """
    # Get the video requested
    video = Video.query.filter(Video.video_id == video_id).one_or_none()

    # Did we find a video?
    if video is not None:
        db.session.delete(video)
        db.session.commit()
        return make_response(
            "Video {video_id} deleted".format(video_id=video_id), 200
        )

    # Otherwise, nope, didn't find that person
    else:
        abort(
            404,
            "Person not found for Id: {video_id}".format(video_id=video_id),
        )

def get_status(video_id):
    """
    This function return video download status
    :param video_id:   Id of the video to delete
    :return:            200 on successful delete, 404 if not found
    """

    video_id = int(video_id)
    dld_thread = app.config["DLD_THREAD"][video_id]

    if dld_thread.is_alive() is True:
        status = "downloading"
        progress = dld_thread.read_status()
    else:
        status = "done"
        progress = "0"
        # clean up the thread and remove it from dict.
        dld_thread.clean_up()
        del app.config["DLD_THREAD"][video_id]

        # find the video entry and mark it as done
        video = Video.query.filter(Video.video_id == video_id).one_or_none()
        print("video:", video)
        if video is not None:
            # # turn the video into a db object
            # schema = VideoSchema()
            # update = schema.load(video, session=db.session).data
            # print("update:", update)
            video.status = "done"
            # merge the new object into the old and commit it to the db
            db.session.merge(video)
            db.session.commit()

    # return json response
    json_response = jsonify(video_id=video_id, status=status, progress=progress)
    return json_response, 200
    # # Otherwise, nope, didn't find that person
    # else:
    #     abort(
    #         404,
    #         "Person not found for Id: {video_id}".format(video_id=video_id),
    #     )
