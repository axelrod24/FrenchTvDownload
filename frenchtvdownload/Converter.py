import logging
import os

from DownloadException import FrTvDownloadException

logger = logging.getLogger("frtvdld")


def CreateMP4(src, dst):
    """
    Creer un mkv a partir de la video existante (cree l'en-tete de la video)
    """
    logger.info("Creation of MP$")
    logger.info("Convert: %s -> %s" % (src, dst))
#    commande = "ffmpeg -hide_banner -i %s -c:a aac -strict -2 -vcodec copy %s" % (src, dst)
    commande = "ffmpeg -hide_banner -i %s -acodec copy -vcodec copy %s" % (src, dst)

    try:
        if (os.system(commande) == 0):
#            os.remove(src)
            logger.info("-> %s" % dst)
        else:
            logger.warning(
                "Problem with FFmpeg ; Video %s is available" % (src))
    except:
        raise FrTvDownloadException("Can't create final MP4")
