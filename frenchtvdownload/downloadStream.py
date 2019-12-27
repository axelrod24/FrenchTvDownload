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

from frtvdld.DownloadException import *
from frtvdld.ColorFormatter import ColorFormatter
from frtvdld.network.NetworkProgParser import networkParserFactory 
from frtvdld.downloader.HLSDownloader import HlsManifestParser, HLSStreamDownloader

from frtvdld.FakeAgent import FakeAgent
from frtvdld.Converter import CreateMP4, FfmpegHLSDownloader
from frtvdld.GlobalRef import LOGGER_NAME

from db.mongoapi import getStreamById, updateStreamById, addVideo, getStreamsByStatus, updateStreamWithError, updateStreamStatus, updateStreamWithMetadata


class StreamMetadata(object):
    def __init__(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key]) 


#
# Main
#
if (__name__ == "__main__"):

    # Arguments de la ligne de commande
    usage = "downloadStream.py [options]"
    parser = argparse.ArgumentParser(usage=usage, description="Download video from FranceTv.fr")
    # parser.add_argument("-b", "--progressbar", action="store_true", default=False,
    #                     help='display download progress')
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help='dispay download information')

    parser.add_argument("-o", "--outDir", action="store", default=".", help='output folder (default .)')

    # parser.add_argument("--noDuplicate", action='store_true', default=False, help="download video only if video id not in Mongo db")
    parser.add_argument("--saveMetadata", action='store_true', default=False, help="save the video metadata in file (.meta)")
    parser.add_argument("--repo", action='store', default='TV', help="define the default folder")

    parser.add_argument("--nocolor", action='store_true', default=False, help='turn of color in terminal')
    parser.add_argument("--version", action='version', version="FrenchTvDownloader %s" % (__version__))
    # parser.add_argument("urlEmission", action="store", help="URL of video to download")
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
    console.setFormatter(ColorFormatter(not args.nocolor))
    logger.addHandler(console)

    # Affiche des infos sur le systeme
    logger.debug("FrenchTvDownload %s with Python %s (%s)" % (__version__, platform.python_version(), platform.machine()))
    logger.debug("OS : %s %s" % (platform.system(), platform.version()))

    # # progress function
    # if (args.progressbar):
    #     progressFnct = lambda x: logger.info("progress : %3d%% - %d/%d" % (min(int((x[0] * 100) / x[1]), 100), x[0], x[1]))
    # else:
    #     progressFnct = lambda x: None


    streams = getStreamsByStatus(status="pending")
    if not streams:
        logger.info("-" * 6)
        logger.info("No pending stream")
        logger.info("=" * 6)
        exit(1)

    for stream in streams:

        try:
            url = stream.url
            networkParser = networkParserFactory(stream.url)
            progMetadata = networkParser.getProgMetaData(url)  

        except Exception as err:
            # log the error and continue with next stream
            logger.error(err.__repr__())
            updateStreamWithError(stream, err.__repr__())
            continue
        
        # create the filename accoding to file meta-data
        # generic video filename (without ext)
        folder = datetime.fromtimestamp(progMetadata.airDate).strftime("%Y-%m-%d_%a")
        dstFullPath = os.path.join(args.outDir, folder)
        
        # create dest folder if doesn't exist
        if os.path.exists(dstFullPath) is False:
            os.mkdir(dstFullPath)
        
        # add filename
        dstFullPath = os.path.join(dstFullPath, progMetadata.filename)
        
        # rename file if it already exist.
        fileIndex = 2
        while os.path.isfile(dstFullPath + ".mp4") is True:
            dstFullPath = os.path.join(args.outDir, progMetadata.filename + "_" + str(fileIndex))
            fileIndex += 1

        # downloading with ffmpeg
        logger.info("++")
        logger.info("Downloading: %s" % (url))
        logger.info("------------")
        updateStreamStatus(stream, "downloading")

        ffmpegHLSDownloader = FfmpegHLSDownloader(url=progMetadata.manifestUrl)
        ffmpegHLSDownloader.downlaodAndConvertFile(dst=dstFullPath + ".mp4")
        logger.info("++")
        logger.info("Download completed: %s" % (url))
        logger.info("Video : %s" % (dstFullPath))
        logger.info("-------")

        # save metadata
        if (args.saveMetadata):
            logger.info("Saving metadata")
            xmlMeta = dicttoxml.dicttoxml(progMetadata._asdict(), attr_type=False)
            dom = minidom.parseString(xmlMeta)
            with open(dstFullPath+".meta", "w") as text_file:
                print(dom.toprettyxml(), file=text_file)

        dstFullPath += ".mp4"
        # save metadata to mongo
        logger.info("Saving video info")
        updateStreamWithMetadata(stream, progMetadata)
        addVideo(dstFullPath, folder, args.repo, progMetadata, stream)

    logger.info("=========================================================")
  
    
