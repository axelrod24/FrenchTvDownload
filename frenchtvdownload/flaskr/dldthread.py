import os, threading, logging, json, shutil, time

from flaskr import models
from flaskr.models import video

from flaskr.config import app

from frtvdld.GlobalRef import LOGGER_NAME
from frtvdld.download import get_video_metadata, download_video, get_error_metadata
from frtvdld.Converter import CreateMP4
from frtvdld.DownloadException import *
from frtvdld import utils

logger = logging.getLogger(LOGGER_NAME)

logger.info("Create ffmpeg thread lock")
ffmpeg_lock = threading.Lock()


def JsonStatus(status, progress=0, message=""):
    return json.dumps({"status":status, "progress":("%d" % progress), "message":message})


class DldThread(threading.Thread):
    def __init__(self, thread_name, url, progMetadata, video_id):
        super().__init__(name=thread_name, target=self.run)
        self.url = url
        self.progMetadata = json.loads(progMetadata)
        self.video_id = video_id
        self.cleaned_up = False
        self.pipein = None

        # create a temp unique folder
        tmp_folder_name = utils.get_random_string()
        self.tmp_path = os.path.join(app.config["TMP_FOLDER"], tmp_folder_name)
        while os.path.exists(self.tmp_path) is True:
            tmp_folder_name = utils.get_random_string()
            self.tmp_path = os.path.join(app.config["TMP_FOLDER"], tmp_folder_name)
        os.mkdir(self.tmp_path)
    
        # create a named pipe, deal with file already exist
        self.pipe_name = os.path.join(self.tmp_path, app.config["PIPE_NAME_HEADER"] % self.getName())
        i=1
        while os.path.exists(self.pipe_name) is True:
            self.pipe_name = os.path.join(self.tmp_path, (app.config["PIPE_NAME_HEADER"]+"_"+str(i)) % self.getName())
            i+=1
        os.mkfifo(self.pipe_name)

        logger.info("Thread:%s, video id:%d, pipe name:%s" % (self.getName(), self.video_id, self.pipe_name))

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
            src_filename = self.progMetadata["filename"] + ".ts"
            ts_file_full_path = os.path.join(self.tmp_path, src_filename)

            try:
                download_video(manifestUrl=self.progMetadata["manifestUrl"], filename=ts_file_full_path, 
                        progressFnct = callback_progress, stopDownloadEvent=self.stop_download_event)

            except FrTvDownloadException as err:
                logger.error("Download error:%s" % err)
                raise err

            # download sucessfuly completed
            logger.info("Video id:%d - downloaded sucessfully" % self.video_id)

            #
            # copy/convert files to final destination folder
            #

            # create folder name as per current date if necessary 
            dst_folder_name = utils.get_datetime_now_string()
            if not os.path.exists(os.path.join(app.config["DST_FOLDER"], dst_folder_name)):
                os.mkdir(os.path.join(app.config["DST_FOLDER"], dst_folder_name))          

            # make dst filename unique
            dst_filename = self.progMetadata["filename"] + ".mp4"
            i=1
            while os.path.exists(os.path.join(app.config["DST_FOLDER"], dst_folder_name, dst_filename)) is True:
                dst_filename = self.progMetadata["filename"] + "_" + str(i) + ".mp4"
                i+=1

            # convert the file
            try:
                self.write_to_pipe(JsonStatus(status="waiting"))
                ffmpeg_lock.acquire()
                dst_file_full_path = os.path.join(app.config["DST_FOLDER"], dst_folder_name, dst_filename)
                self.write_to_pipe(JsonStatus(status="converting"))
                CreateMP4(ts_file_full_path, dst_file_full_path)
                ffmpeg_lock.release()
            except Exception as err:
                ffmpeg_lock.release()
                raise err

            # find the video entry and mark it as "done"
            models.video.update_video_by_id(self.video_id, status="done", folder_name=dst_folder_name, video_file_name=dst_filename)

            # write "done" status.
            self.write_to_pipe(JsonStatus(status="done"))

            # conversion & copy sucessfuly completed
            logger.info("Video id:%d - conversion sucessfully" % self.video_id)

        except Exception as err:
            # download interupted by user, set video status to pending to allow re-download
            if isinstance(err, FrTvDwnUserInterruption):
                error_type = "interrupted"
                models.video.update_video_by_id(self.video_id, status="pending")
            else:
                error_type = "error"
                # update mdata with the error message
                self.progMetadata["errorMsg"] = "%s" % err
                models.video.update_video_by_id(self.video_id, status="error", mdata=self.progMetadata)

            logger.info(err)
            self.write_to_pipe(JsonStatus(status=error_type, message="%s" % err))

        # thread terminate on success or error, wait for clean-up() to be called.
        while(not self.cleaned_up):
            time.sleep(1)
        
    # def start(self):
    #     # start the thread and read from the pipe
    #     self.pipein = open(self.pipe_name, 'r')
    #     super().start()

    def cleanup(self):
        os.remove(self.pipe_name) 
        shutil.rmtree(self.tmp_path)
        self.cleaned_up = True

    def write_to_pipe(self, msg):
        # add msg to pipe with line termination
        pipeout = os.open(self.pipe_name, os.O_WRONLY)
        os.write(pipeout, str.encode(("%s\n"%msg))) 
        os.close(pipeout)

    def read_status(self):
        # read the pipe and return last line
        if self.pipein is None:
            self.pipein = open(self.pipe_name, 'r')
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


