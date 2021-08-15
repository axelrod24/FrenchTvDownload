import logging
import os
import subprocess
import shlex

from frtvdld.DownloadException import FrTvDownloadException
from frtvdld.GlobalRef import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def CreateMP4(src, dst):
  """
  convert to MP4
  """
  logger.info("Creation of MP$")
  logger.info("Convert: %s -> %s" % (src, dst))
  commande = "ffmpeg -hide_banner -i %s -acodec copy -vcodec copy %s" % (src, dst)

  try:
    if (os.system(commande) == 0):
      logger.info("-> %s" % dst)
    else:
      logger.warning("Problem with FFmpeg ; Video %s is available" % (src))
      raise FrTvDownloadException("Error running FFmpeg, video might be available:"+src)

  except Exception as err:
    raise FrTvDownloadException("Can't create final MP4. "+err.__repr__())


class FfmpegHLSDownloader(object):
  def __init__(self, url, userAgent):
    self.manifestUrl = url
    self.userAgent = userAgent

  def downloadAndConvertFile(self, dst):
    log_file = dst.split(".mp4")[0]+".log"
    command = 'ffmpeg -hide_banner -user_agent "%s" -loglevel info -i "%s" -acodec copy -vcodec copy %s' % (self.userAgent, self.manifestUrl , dst)
    command_args = shlex.split(command)
    #command = ['ffmpeg', '-hide_banner', '-user_agent', '%s'%(self.userAgent), '-loglevel', 'info', '-i', '%s'%(self.manifestUrl), '-acodec', 'copy', '-vcodec', 'copy', dst]
    logger.info("ffmpeg command")
    logger.info(command_args)
    try:
      with open(log_file, 'w') as stderr_file:
        process_output = subprocess.run(command_args, stdout=subprocess.PIPE, stderr=stderr_file, text=True)

      #if (os.system(command) == 0):
      if (process_output.returncode==0):
        logger.info("-> %s" % dst)
        logger.info("-> %s" % log_file)
      else:
        logger.warning("Problem with FFmpeg: %s"%process_output.stdout)
        raise FrTvDownloadException("Error running: FFmpeg %s"%process_output.stdout)

    except Exception as err:
      raise FrTvDownloadException("Can't create final MP4. "+err.__repr__())
