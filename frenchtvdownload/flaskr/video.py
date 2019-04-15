
import os, threading, logging, json
from flask import make_response, abort, jsonify

from flaskr.config import db, app
from flaskr import models

from frtvdld.GlobalRef import LOGGER_NAME
from frtvdld.download import get_video_metadata, download_video, get_error_metadata
from frtvdld.DownloadException import *

logger = logging.getLogger(LOGGER_NAME)


def JsonStatus(status, progress=0, message=""):
    return json.dumps({"status":status, "progress":("%d" % progress), "message":message})

class DldThread():
    def __init__(self, url, progMetadata, video_id):
        self.thread = threading.Thread(target=self.run)
        self.url = url
        self.progMetadata = json.loads(progMetadata)
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
            metadata = download_video(self.progMetadata, base_folder=app.config["DLD_FOLDER"], progressFnct = callback_progress, stopDownloadEvent=self.stop_download_event)

            # download sucessfuly completed
            logger.info("Video id:%d - downloaded sucessfully" % self.video_id)

            # find the video entry and mark it as "done"
            models.update_video_by_id(self.video_id, status="done", mdata=metadata)

            # write "done" status.
            self.write_to_pipe(JsonStatus(status="done"))

        except Exception as err:
            # download interupted by user
            if isinstance(err, FrTvDwnUserInterruption):
                # assuming file cleaning as been done by downloaded.  Mark video as pending and notify client of erro/interrupted status
                error_type = "interrupted"
                status = "pending"
            else:
                error_type = "error"
                status = "error"

            models.update_video_by_id(self.video_id, status=status)

            logger.info(err)
            self.write_to_pipe(JsonStatus(status=error_type, message="%s" % err))


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
    data = models.get_all_video()
    return data


def read_one(video_id):
    video_id = int(video_id)
    video = models.get_video_by_id(video_id)
    return video


def add_url(url):
    existing_url = models.get_video_by_url(url)

    # can we insert this video?
    if existing_url is None:
        # get video metadata
        try:
            metadata = get_video_metadata(url)
            if metadata.manifestUrl is None:
                status = "not_available"
            else:
                status = "pending"

        except Exception as err:
            # if isinstance(err, FrTvDwnVideoNotFound):
            #     error = "Can't find video"
            # elif isinstance(err, FrTvDwnPageParsingError):
            #     error = "Can't get or parse video ID page"
            # elif isinstance(err, FrTvDwnManifestError):
            #     error = "Can't get manifest URL (video link expired)"
            # elif isinstance(err, FrTvDwnMetaDataParsingError):
            #     error = "Can't parse video metadata"
            # else:
            #     error = "Unknown error getting metadata"
            
            error = err.__repr__()
            logger.error(error)
            errMetadata = get_error_metadata(url, error)
            metadata = errMetadata.getMetadata()
            status = "error"

        finally:
            video = models.add_new_video(url=url, status=status, mdata=json.dumps(metadata._asdict()))
            return video

    # video exists already
    return None

        
def download(video_id):
    video_id = int(video_id)
    video = models.update_video_by_id(video_id, status="downloading")
    if video is not None:
        # create, store the thread and start it 
        dld_thread = DldThread(video["url"], video["mdata"], video["video_id"])
        app.config["DLD_THREAD"][video["video_id"]] = dld_thread
        dld_thread.start() 

        return video

    return None


def cancel(video_id):
    video_id = int(video_id)
    dld_thread = app.config["DLD_THREAD"].get(video_id, None)
    if dld_thread is None:
        return False

    dld_thread.cancel_download()
    return True
   

def delete(video_id):
    # Get the video requested
    video = models.delete_video_by_id(video_id)
    return video


def get_status(video_id):
    video_id = int(video_id)
    dld_thread = app.config["DLD_THREAD"].get(video_id, None)
    if dld_thread is None:
        return None

    # we read download progress
    dld_status = dld_thread.read_status()
    logger.debug("dld_status is %s" % dld_status)
    status = json.loads(dld_status)
    logger.debug("status is %s" % status)

    if status["status"] in ["done", "error"]:
        # clean up the thread and remove it from dict.
        dld_thread.cleanup() 
        del app.config["DLD_THREAD"][video_id]

    return {"video_id":video_id, "status":dld_status}



