
import os, threading, logging
from flask import make_response, abort, jsonify

from config import db, app
from models import Video, VideoSchema 

from frtvdld.GlobalRef import LOGGER_NAME
from frtvdld.download import download_video
from frtvdld.DownloadException import *

logger = logging.getLogger(LOGGER_NAME)

class DldThread():
    def __init__(self, url, video_id):
        self.thread = threading.Thread(target=self.run)
        self.url = url
        self.video_id = video_id

        # create a named pipe, deal with file already exist
        self.pipe_name = os.path.join(app.config["DLD_FOLDER"], app.config["PIPE_NAME_HEADER"] % self.thread.name)
        i=1
        while os.path.exists(self.pipe_name) is True:
            self.pipe_name = os.path.join(app.config["DLD_FOLDER"], (app.config["PIPE_NAME_HEADER"]+"_"+str(i)) % self.thread.name)
            i+=1

        os.mkfifo(self.pipe_name)
        logger.info("video id:{video_id}, pipe name:{pipe_name}".format(video_id=self.video_id, pipe_name=self.pipe_name))

        # create the stop event
        self.stop_download_event=threading.Event()

    def run(self):

        # call back function to log download progress to client thread        
        def callback_progress(x):
            # log to console
            logger.info("Video id:%d - progress:%3d - %d/%d" % (self.video_id, min(int((x[0] * 100) / x[1]), 100), x[0], x[1]))
            # write to pipe for client update
            self.write_to_pipe("%d\n" % (x[1]-x[0]+1))

        try:
            info_msg = "done"
            download_video(self.url, base_folder=app.config["DLD_FOLDER"], progressFnct = callback_progress, stopDownloadEvent=self.stop_download_event)

            # download sucessfuly completed
            logger.info("Video id:%d - downloaded sucessfully" % self.video_id)

            # find the video entry and mark it as "done"
            video = Video.query.filter(Video.video_id == self.video_id).one_or_none()
            if video is not None:
                video.status = "done"
                db.session.merge(video)
                db.session.commit()

            # write "done" status.
            self.write_to_pipe("done")


        except FrTvDownloadException as excepErr:
            if isinstance(excepErr, FrTvDwnUserInterruption):
                info_msg = "interrupted"
                error_msg = "Download Interrupted by user"
            elif isinstance(excepErr, FrTvDwnVideoNotFound):
                info_msg = "error"
                error_msg = "Can't find video: %s" % self.url
            elif isinstance(excepErr, FrTvDwnPageParsingError):
                info_msg = "error"
                error_msg = "Can't get or parse video ID page: %s" % self.url
            elif isinstance(excepErr, FrTvDwnManifestUrlNotFoundError):
                info_msg = "error"
                error_msg = "Can't parse video metadata: %s" % self.url
            elif isinstance(excepErr, FrTvDwnMetaDataParsingError):
                info_msg = "error"
                error_msg = "Can't get manifest URL: %s" % self.url
            else:
                info_msg = "error"
                error_msg = "Unknown error getting metadata for %s" % self.url

            # assuming file cleaning as been done by downloaded.  Mark video as pending and notify client of erro/interrupted status
            video = Video.query.filter(Video.video_id == self.video_id).one_or_none()
            if video is not None:
                video.status = "pending"
                db.session.merge(video)
                db.session.commit()

            logger.info(error_msg)
            self.write_to_pipe(info_msg)


    def start(self):
        # start the thread and read from the pipe
        self.thread.start()
        self.pipein = open(self.pipe_name, 'r')

    def is_alive(self):
        return self.thread.is_alive() 

    def write_to_pipe(self, msg):
        pipeout = os.open(self.pipe_name, os.O_WRONLY)
        os.write(pipeout, str.encode(msg))
        os.close(pipeout)

    def read_status(self):
        lines = self.pipein.readlines()
        logger.debug("line is:%s" % lines)
        status = lines[-1:]
        return status

    def cancel_download(self):
        logger.info("Cancel download for video id:%d" % (self.video_id))
        self.stop_download_event.set()

    def cleanup(self):
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
    logger.debug("url is : "+url)
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

        # Serialize and return the newly created video in the response
        schema = VideoSchema()
        data = schema.dump(video).data

        return data, 201

    # Otherwise, nope, person exists already
    else:
        abort(
            409,
            "Can't find video {video_id}".format(video_id=video_id),
        )

def cancel(video_id):
    """
    This function cancel video download
    :param video_id:   Id of the video 
    :return:            200 on successful cancel, 404 if not found
    """

    video_id = int(video_id)
    dld_thread = app.config["DLD_THREAD"][video_id]

    # \TODO manage error here, dld_thread can not be found

    dld_thread.cancel_download()

    return {}, 200
   

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

    dld_status = dld_thread.read_status()

    # we read download progress
    logger.debug("dld_status is %s" % dld_status)
    if dld_status not in [["done"], ["error"], ["interrupted"]]:

        progress = dld_status
            # if nothing is the pipe, we assume no new update
        if not progress:
            status = "no_update"
        else:
            status = "downloading"

    else:
        # download process completed either successfully or unsuccessfully 
        progress = "0"
        status = dld_status[0]
        
        # clean up the thread and remove it from dict.
        dld_thread.cleanup() 
        del app.config["DLD_THREAD"][video_id]

    # return json response
    json_response = jsonify(video_id=video_id, status=status, progress=progress)
    return json_response, 200
