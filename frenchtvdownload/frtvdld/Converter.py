import logging
import os
import subprocess

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
    #command = ['ffmpeg', '-hide_banner', '-user_agent', '%s'%(self.userAgent), '-loglevel', 'info', '-i', '%s'%(self.manifestUrl), '-acodec', 'copy', '-vcodec', 'copy', dst]
    logger.info(command)
    try:
      #with open(log_file, 'w') as stdout_file:
      #  process_output = subprocess.run(command, stdout=stdout_file, stderr=subprocess.STDOUT, text=True)

      if (os.system(command) == 0):
      #if (process_output.stderr==None):
        logger.info("-> %s" % dst)
      else:
        logger.warning("Problem with FFmpeg: %s"%process_output.stderr)
        raise FrTvDownloadException("Error running: FFmpeg %s"%process_output.stderr)
      
    except Exception as err:
      raise FrTvDownloadException("Can't create final MP4. "+err.__repr__())
