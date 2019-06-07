
import os, threading, logging, json
from flask import make_response, abort, jsonify

from flaskr.config import db, app
from flaskr import models
from flaskr.models import video, dldagent
from flaskr import dldthread

from frtvdld.GlobalRef import LOGGER_NAME
from frtvdld.download import get_video_metadata, download_video, get_error_metadata
from frtvdld.DownloadException import *
from frtvdld import utils

logger = logging.getLogger(LOGGER_NAME)

logger.info("Create download thread lock")
thread_lock = threading.Lock()

THREAD_NAME_PREFIX="Thread_video_id_%d"

def read_all():
    data = models.video.get_all_video()
    return data


def read_one(video_id):
    video_id = int(video_id)
    video = models.video.get_video_by_id(video_id)
    return video


def add_url(url):
    existing_url = models.video.get_video_by_url(url)

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
            error = err.__repr__()
            logger.error(error)
            errMetadata = get_error_metadata(url, error)
            metadata = errMetadata.getMetadata()
            status = "error"

        finally:
            video = models.video.add_new_video(url=url, status=status, mdata=json.dumps(metadata._asdict()))
            return video

    # video exists already
    return None

        
def download(video_id):
    video_id = int(video_id)
    video = models.video.update_video_by_id(video_id, status="downloading")
    if video is not None:
        # create the thread, store it and start it 
        thread_name = THREAD_NAME_PREFIX % video_id
        thread_lock.acquire()
        dld_thread = dldthread.DldThread(thread_name, video["url"], video["mdata"], video["video_id"])
        dld_thread.start()
        thread_lock.release()
        return video

    return None


def cancel(video_id):
    video_id = int(video_id)
    dld_thread = get_thread_agent_by_video_id(video_id)
    if dld_thread is None:
        logger.warning("Cancel: No download thread for id:%d" % video_id)
        return False

    dld_thread.cancel_download()
    return True


def get_status(video_id):
    video_id = int(video_id)
    dld_thread = get_thread_agent_by_video_id(video_id)
    if dld_thread is None:
        logger.warning("get_status: No download thread for id:%d" % video_id)
        return None

    # we read download progress as a json string and convert it to a dict.
    dld_status = dld_thread.read_status()
    status = json.loads(dld_status)
    logger.debug("status is %s" % status)

    # if donwload complete or error, clean up the thread and remove it from dict.
    if status["status"] in ["done", "error", "interrupted"]:
        dld_thread.cleanup() 

    # return latest status
    return {"video_id":video_id, "status":dld_status}


def delete(video_id):
    # Get the video requested
    video = models.video.delete_video_by_id(video_id)
    return video


def get_thread_agent_by_video_id(video_id):
    thread_name = THREAD_NAME_PREFIX % video_id
    thread_lock.acquire()
    thread_list = threading.enumerate()
    thread_lock.release()
    for t in thread_list:
        if t.getName() == thread_name:
            return t
    return None


