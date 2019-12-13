import logging
import os

from frtvdld.DownloadException import FrTvDownloadException

logger = logging.getLogger("frtvdld")



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
  def __init__(self, url):
    self.manifestUrl = url

  def downlaodAndConvertFile(self, dst):
    command = "ffmpeg -hide_banner -i %s -acodec copy -vcodec copy %s" % (self.manifestUrl , dst)
    try:
      if (os.system(command) == 0):
        logger.info("-> %s" % dst)
      else:
        logger.warning("Problem with FFmpeg")
        raise FrTvDownloadException("Error running FFmpeg")
      
    except Exception as err:
      raise FrTvDownloadException("Can't create final MP4. "+err.__repr__())