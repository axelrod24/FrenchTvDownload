#!/usr/bin/python3
# # -*- coding:Utf-8 -*-

import os
v_env_base_path = os.environ.get('VIRTUAL_ENV', '../.venv')
activate_this = os.path.join(v_env_base_path,'bin/activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

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
from urllib.parse import urlparse

from frtvdld.DownloadException import *
from frtvdld.ColorFormatter import ColorFormatter
from frtvdld.network.NetworkProgParser import networkParserFactory 
from frtvdld.downloader.HLSDownloader import HlsManifestParser, HLSStreamDownloader

from frtvdld.FakeAgent import FakeAgent
from frtvdld.Converter import CreateMP4, FfmpegHLSDownloader
from frtvdld.GlobalRef import LOGGER_NAME

from db.mongoapi import addStream, getStreamByUrl
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
    parser.add_argument("--programCode", action="store", default="", help='set the program code for that video or collection')
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

        # use code program passed as argument or extract the last part of URL as code program
        parsedUrl = urlparse(url)
        programCode = args.programCode
        if len(programCode)==0:
            programCode = parsedUrl.path.strip('/').split('/').pop()

        networkName = parsedUrl.hostname

        for url in listOfUrls:
            logger.info("-" * 6)
            stream = getStreamByUrl(url)
            if (stream):  #and stream.status=="done"):
                if (stream.status=="error" and len(stream.lastErrors)<3):
                    stream.status = "pending"
                    stream.save()
                    logger.info("Trying download again:%d" % len(stream.lastErrors))
                else:
                    logger.info("Duplicate. Continue ...")
                    logger.info("Url: %s" % (url))

                logger.info("=" * 6)
                continue  

            # add the Stream as pending.
            logger.info("Adding pending stream: %s" % (url))
            stream = addStream(url, "pending")
            stream.progCode = programCode
            stream.networkName = networkName
            stream.save()
            logger.info("=" * 6)

    except Exception as err:
        logger.error(err.__repr__())
        exit()
 
    logger.info("=========================================================")
  
    
