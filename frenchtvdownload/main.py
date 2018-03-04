#!/usr/bin/env python2
# -*- coding:Utf-8 -*-

#
# Infos
#

__author__ = "Alexrod24"
__license__ = "GPL 2"
__version__ = "0.1"
__url__ = "https://github.com/axelrod24/FrenchTvDownload"


import argparse
import logging
import platform
import os
import sys

from ColorFormatter import ColorFormatter
from francetv.francetv import FranceTvDownloader
from FakeAgent import FakeAgent
from Converter import CreateMP4
from GlobalRef import LOGGER_NAME
#
# Main
#

REG_EXP = 'www.france.tv/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

if (__name__ == "__main__"):

    # Arguments de la ligne de commande
    usage = "main.py [options] urlToVideo"
    parser = argparse.ArgumentParser(usage=usage, description="Download video from FranceTv.fr")
    parser.add_argument("-b", "--progressbar", action="store_true", default=False,
                        help='display download progress')
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help='dispay download information')

    parser.add_argument("-o", "--outDir", action="store", default=".", help='output folder (default .)')
    # parser.add_argument("-x", "--extractedUrl", action="store_true", default=False, help='extract Selection URL (france.tv)')

    parser.add_argument("--nocolor", action='store_true', default=False, help='turn of color in terminal')
    parser.add_argument("--version", action='version', version="FrenchTvDownloader %s" % (__version__))
    parser.add_argument("urlEmission", action="store", help="URL of video to download")
    args = parser.parse_args()

    # Mise en place du logger
    logger = logging.getLogger(LOGGER_NAME)
    console = logging.StreamHandler(sys.stdout)
    if (args.verbose):
        logger.setLevel(logging.DEBUG)
        console.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        console.setLevel(logging.INFO)
    console.setFormatter(ColorFormatter(not args.nocolor))
    logger.addHandler(console)

    # Affiche des infos sur le systeme
    logger.debug("FrenchTvDownload %s with Python %s (%s)" % (__version__, platform.python_version(), platform.machine()))
    logger.debug("OS : %s %s" % (platform.system(), platform.version()))

    # if (re.match("https://www.france.tv/[^\.]+?\.html", args.urlEmission) is None):
    #     logger.error("L'URL \"%s\" n'est pas valide" % (args.urlEmission))
    #     sys.exit(-1)


    # progress function
    if (args.progressbar):
        progressFnct = lambda x: logger.info("progress : %3d %%" % (x))
    else:
        progressFnct = lambda x: None

    logger.info(args.urlEmission)

    downloader = FranceTvDownloader(url=args.urlEmission, fakeAgent=FakeAgent())

    videoFullPath = downloader.download(progressFnct=progressFnct)

    # convert to mp4
    if videoFullPath is not None:
        fname = os.path.basename(videoFullPath).replace(".ts", ".mp4")
        dstFullPath = os.path.join(args.outDir, fname)

        # rename file if it already exist.
        fileIndex = 1
        while os.path.isfile(dstFullPath) is True:
            basenamePath = dstFullPath.split(".mp4")[0]
            dstFullPath = basenamePath + "_" + str(fileIndex) + ".mp4"
            fileIndex += 1

        CreateMP4(videoFullPath, dstFullPath)

