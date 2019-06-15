
import os, threading, logging, json

from flask import make_response, abort, jsonify

from flaskr import models
from flaskr.config import app
from flaskr.models import video, dldagent
from flaskr import threadmgr

from frtvdld.GlobalRef import LOGGER_NAME
from frtvdld.download import get_video_metadata, download_video, get_error_metadata
from frtvdld.DownloadException import *
from frtvdld import utils

MAX_CONCURENT_DOWNLOAD = 5
ASYNC_DOWNLOAD_INTERVAL = 30

logger = logging.getLogger(LOGGER_NAME)

# start async download loop
_async_download_loop()


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

        
def async_download(video_id):
    video_id = int(video_id)
    # if too many concurent downlaod, add to the queue of async dowwnload
    nbr_concurent_download = _get_number_of_concurent_download()
    if nbr_concurent_download >= MAX_CONCURENT_DOWNLOAD:
        video = models.video.update_video_by_id(video_id, status="queued")
        app.config["DLD_QUEUE"].put(video_id)
        return video

    video = models.video.update_video_by_id(video_id, status="downloading")
    if video is not None:
        # create the thread, store it and start it 
        threadmgr.create_and_start_download_thread(video_id, video)
        return video

    return None


def cancel(video_id):
    video_id = int(video_id)
    dld_thread = threadmgr.get_thread_agent_by_video_id(video_id)
    if dld_thread is None:
        logger.warning("Cancel: No download thread for id:%d" % video_id)
        return False

    dld_thread.cancel_download()
    threadmgr.remove_thread_by_video_id(video_id)
    return True


def get_status(video_id):
    video_id = int(video_id)
    dld_thread = threadmgr.get_thread_agent_by_video_id(video_id)
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
        threadmgr.remove_thread_by_video_id(video_id)

    # return latest status
    return {"video_id":video_id, "status":dld_status}


def delete(video_id):
    # Get the video requested
    video = models.video.delete_video_by_id(video_id)
    return video


def _download(video_id):
    video_id = int(video_id)
    video = models.video.update_video_by_id(video_id, status="downloading")
    if video is not None:
        # create the thread, store it and start it 
        threadmgr.create_and_start_download_thread(video_id, video)
        return video

    return None


def _get_number_of_concurent_download():
    # check number of concurent download
    dowload_list = models.video.get_video_by_status("downloading")
    if dowload_list is not None:
        return len(dowload_list)
    
    return 0


def _async_download_loop():
    dld_queue = app.config["DLD_QUEUE"]
    if dld_queue.empty():
        threading.Timer(ASYNC_DOWNLOAD_INTERVAL, _async_download_loop)
        return 

    # check number of concurent download
    nbr_concurent_download = _get_number_of_concurent_download()
    if nbr_concurent_download >= MAX_CONCURENT_DOWNLOAD:
        threading.Timer(ASYNC_DOWNLOAD_INTERVAL, _async_download_loop)
        return 

    while (nbr_concurent_download < MAX_CONCURENT_DOWNLOAD and not dld_queue.empty()):
        next_id = dld_queue.get()
        _download(next_id)
        nbr_concurent_download+=1
