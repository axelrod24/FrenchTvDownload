
import os, threading, logging, json
from flask import make_response, abort, jsonify

from flaskr.config import db, app
from flaskr.models import VideoModel, VideoSchema 

from frtvdld.GlobalRef import LOGGER_NAME
from frtvdld.download import download_video
from frtvdld.DownloadException import *

logger = logging.getLogger(LOGGER_NAME)

def JsonStatus(status, progress):
    return json.dumps({"status":status, "progress":("%d" % progress)})

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
            self.write_to_pipe(JsonStatus(status="downloading", progress = (x[1]-x[0]+1)))

        try:
            info_msg = "done"
            metadata = download_video(self.url, base_folder=app.config["DLD_FOLDER"], progressFnct = callback_progress, stopDownloadEvent=self.stop_download_event)

            # download sucessfuly completed
            logger.info("Video id:%d - downloaded sucessfully" % self.video_id)

            # find the video entry and mark it as "done"
            _updateVideoModelAndMetadata(video_id = self.video_id, status = "done", metadata=metadata)

            # write "done" status.
            self.write_to_pipe(JsonStatus(status="done", progress = 0))

        except FrTvDownloadException as excepErr:
            if isinstance(excepErr, FrTvDwnUserInterruption):
                info_msg = "interrupted"
                error_msg = "Download Interrupted by user"
            elif isinstance(excepErr, FrTvDwnVideoNotFound):
                info_msg = "not_available"
                error_msg = "Can't find video: %s" % self.url
            elif isinstance(excepErr, FrTvDwnPageParsingError):
                info_msg = "error"
                error_msg = "Can't get or parse video ID page: %s" % self.url
            elif isinstance(excepErr, FrTvDwnManifestUrlNotFoundError):
                info_msg = "not_available"
                error_msg = "Can't parse video metadata: %s" % self.url
            elif isinstance(excepErr, FrTvDwnMetaDataParsingError):
                info_msg = "error"
                error_msg = "Can't get manifest URL: %s" % self.url
            else:
                info_msg = "error"
                error_msg = "Unknown error getting metadata for %s" % self.url

            # assuming file cleaning as been done by downloaded.  Mark video as pending and notify client of erro/interrupted status
            if info_msg in ["interrupted"]:
                status = "pending"
            else:
                status = info_msg

            _updateVideoModelAndMetadata(self.video_id, status)

            logger.info(error_msg)
            self.write_to_pipe(JsonStatus(status=info_msg, progress = 0))


    def start(self):
        # start the thread and read from the pipe
        self.thread.start()
        self.pipein = open(self.pipe_name, 'r')

    def is_alive(self):
        return self.thread.is_alive() 

    def write_to_pipe(self, msg):
        pipeout = os.open(self.pipe_name, os.O_WRONLY)
        # add msg to pipe with line termination
        os.write(pipeout, str.encode(("%s\n"%msg))) 
        os.close(pipeout)

    def read_status(self):
        lines = self.pipein.readlines()
        logger.debug("line is:%s" % lines)
        
        status = lines[-1:]
        # if no progress, no update
        if (len(status) == 0):
            return JsonStatus(status="no_update", progress = 0)

        return status[0]

    def cancel_download(self):
        logger.info("Cancel download for video id:%d" % (self.video_id))
        self.stop_download_event.set()

    def cleanup(self):
        os.remove(self.pipe_name) 


def read_all():
    # Create the list of video from our data
    video = VideoModel.query.order_by(VideoModel.timestamp).all()

    # Serialize the data for the response
    video_schema = VideoSchema(many=True)
    data = video_schema.dump(video).data
    return data


def read_one(video_id):

    # Create the list of video from our data
    video_id = int(video_id)
    video = VideoModel.query.filter(VideoModel.video_id == video_id).one_or_none()

    # Did we find a video?
    if video is not None:
            
        # Serialize the data for the response
        video_schema = VideoSchema()
        data = video_schema.dump(video).data
        return data, 200
    else:
        abort(
            409,
            "Can't find video {video_id}".format(video_id=video_id),
        )


def addurl(url):
    logger.debug("url is : "+url)

    existing_url = (
        VideoModel.query.filter(VideoModel.url == url).one_or_none()
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

    video_id = int(video_id)
    video = _updateVideoModelAndMetadata(video_id, "downloading")

    if video is not None:
        # create, store the thread and start it 
        dld_thread = DldThread(video.url, video.video_id)
        app.config["DLD_THREAD"][video.video_id] = dld_thread
        dld_thread.start() 

        # Serialize and return the newly created video in the response
        schema = VideoSchema()
        data = schema.dump(video).data

        return data

    # Otherwise, nope, person exists already
    else:
        return None


def cancel(video_id):

    video_id = int(video_id)
    dld_thread = app.config["DLD_THREAD"][video_id]

    # \TODO manage error here, dld_thread can not be found

    dld_thread.cancel_download()

    return {}, 200
   

def delete(video_id):
    # Get the video requested
    video = VideoModel.query.filter(VideoModel.video_id == video_id).one_or_none()

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
    video_id = int(video_id)
    dld_thread = app.config["DLD_THREAD"][video_id]

    # we read download progress
    dld_status = dld_thread.read_status()
    logger.debug("dld_status is %s" % dld_status)
    status = json.loads(dld_status)
    logger.debug("status is %s" % status)

    if status["status"] == "done":
        # clean up the thread and remove it from dict.
        dld_thread.cleanup() 
        del app.config["DLD_THREAD"][video_id]

    return {"video_id":video_id, "status":dld_status}


def _updateVideoModelAndMetadata(video_id, status, metadata=None):
    video = VideoModel.query.filter(VideoModel.video_id == video_id).one_or_none()
    if video is not None:
        video.status = status

        if metadata is not None:
            video.mdata = json.dumps(metadata)
        else:
            video.mdata = ''

        db.session.merge(video)
        db.session.commit()
        return video
    
    return None

