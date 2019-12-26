#!/usr/bin/python3
# # -*- coding:Utf-8 -*-

# import sys
# print (sys.version)
# print (sys.path)

activate_this = '../.venv/bin/activate_this.py'
#activate_this = '/home/lbr/Wks/FrenchTvDownload/.venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# import sys
# print (sys.version)
# print (sys.path)

#
# Infos
#
__author__ = "Alexrod24"
__license__ = "GPL 2"
__version__ = "0.1"
__url__ = "https://github.com/axelrod24/FrenchTvDownload"

import yaml
import argparse
import logging
import platform
import os
import sys
import tempfile
import shutil
import dicttoxml
import requests
import json

from datetime import datetime
from xml.dom import minidom

from frtvdld.DownloadException import *
from frtvdld.ColorFormatter import ColorFormatter
from frtvdld.network.NetworkProgParser import networkParserFactory 
from frtvdld.downloader.HLSDownloader import HlsManifestParser, HLSStreamDownloader

from frtvdld.FakeAgent import FakeAgent
from frtvdld.Converter import CreateMP4, FfmpegHLSDownloader
from frtvdld.GlobalRef import LOGGER_NAME

from db.mongoapi import getStreamById, updateStreamById, addVideo
#
# Main
#

if (__name__ == "__main__"):

    # Arguments de la ligne de commande
    usage = "fetchCollection.py [options] urlToCollection"
    parser = argparse.ArgumentParser(usage=usage, description="Download video from FranceTv.fr")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help='dispay download information')

    parser.add_argument("-i", "--input", action="store", choices=['url', 'mongo'], default="url", help='input source url or mongo')
    parser.add_argument("--nbrVideo", action="store", default="1", help='number of video link to fech (default 1), -1 means all')


    # parser.add_argument("--noDuplicate", action='store_true', default=False, help="download video only if video id not in Mongo db")
    # parser.add_argument("--saveMetadata", action='store', choices=['file', 'mongo'], nargs="+", help="save the video metadata in file (.meta) and/or mongo")
    # parser.add_argument("--parseCollection", action='store_true', default=False, help="return a list of video URL which are part of a collection")
    # parser.add_argument("--repo", action='store', default='TV', help="define the default folder")

    # parser.add_argument("--nocolor", action='store_true', default=False, help='turn of color in terminal')
    # parser.add_argument("--version", action='version', version="FrenchTvDownloader %s" % (__version__))
    parser.add_argument("urlEmission", action="store", help="URL of video to download")
    args = parser.parse_args()

    # set logger
    logger = logging.getLogger(LOGGER_NAME)
    console = logging.StreamHandler(sys.stdout)
    if (args.verbose):
        logger.setLevel(logging.DEBUG)
        console.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        console.setLevel(logging.INFO)
    console.setFormatter(ColorFormatter(True))
    logger.addHandler(console)

    # Affiche des infos sur le systeme
    logger.debug("Python %s (%s)" % (platform.python_version(), platform.machine()))
    logger.debug("OS : %s %s" % (platform.system(), platform.version()))

    if (args.input == 'mongo'):
        logger.error("input mongo not supported yet")
        exit(1)

    try:
        url = args.urlEmission
        networkParser = networkParserFactory(url)
        listOfUrls = networkParser.parseCollection(url, int(args.nbrVideo))
       
        for url in listOfUrls:
            pmdata = networkParser.getProgMetaData(url)
            stream = getStreamById(pmdata.videoId)
            if (stream and stream.status=="done"):
                logger.info("Duplicate. Continue ...")
                logger.info("Url: %s" % (url))
                logger.info("VideoId: %s" % (pmdata.videoId))
                logger.info("======")
                continue  
            
            # add the Stream as pending.
            logger.info("Adding pending stream: %s" % (url))
            updateStreamById(pmdata.videoId, pmdata, status="pending")
            logger.info("======")

    except Exception as err:
        logger.error(err.__repr__())
        exit()
 
    logger.info("=========================================================")
  
    
