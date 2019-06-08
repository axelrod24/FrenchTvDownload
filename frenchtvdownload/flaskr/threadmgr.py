import os, threading, logging, json

from flaskr.config import db, app
from flaskr import dldthread

from frtvdld.GlobalRef import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

logger.info("Create download thread lock")
thread_lock = threading.Lock()

THREAD_NAME_PREFIX="Thread_video_id_%d"

def create_and_start_download_thread(video_id, video):
    thread_name = THREAD_NAME_PREFIX % video_id
    thread_lock.acquire()
    dld_thread = dldthread.DldThread(thread_name, video["url"], video["mdata"], video["video_id"])
    dld_thread.start()
    app.config["DLD_THREAD"][thread_name] = dld_thread
    thread_lock.release()


def get_thread_agent_by_video_id(video_id):
    thread_name = THREAD_NAME_PREFIX % video_id
    thread_lock.acquire()
    logger.info("video_id:%d, dld thread:%s" % (video_id, app.config["DLD_THREAD"].keys()))
    dld_thread = app.config["DLD_THREAD"].get(thread_name, None)
    thread_lock.release()
    return dld_thread

def remove_thread_by_video_id(video_id):
    thread_name = THREAD_NAME_PREFIX % video_id
    thread_lock.acquire()
    if app.config["DLD_THREAD"].get(thread_name) is not None:
        del app.config["DLD_THREAD"][thread_name]
    thread_lock.release()


