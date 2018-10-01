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
import tempfile
import shutil

from urllib.parse import urlparse

from ColorFormatter import ColorFormatter
from network.NetworkProgParser import NetworkProgParser
from downloader.HLSDownloader import HlsManifestParser, HLSStreamDownloader

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
        progressFnct = lambda x: logger.info("progress : %3d%% - %d/%d" % (min(int((x[0] * 100) / x[1]), 100), x[0], x[1]))
    else:
        progressFnct = lambda x: None

    logger.info(args.urlEmission)
    parsed_uri = urlparse(args.urlEmission)

    if parsed_uri.netloc == "www.france.tv" or parsed_uri.netloc == "france.tv":
        networkParser = NetworkProgParser(NetworkProgParser.FRANCETV)
    elif parsed_uri.netloc == "www.arte.tv" or parsed_uri.netloc == "arte.tv":
        networkParser = NetworkProgParser(NetworkProgParser.ARTETV)
    elif parsed_uri.netloc == "www.tf1.fr" or parsed_uri.netloc == "tf1.fr":
        networkParser = NetworkProgParser(NetworkProgParser.TF1)
    else:
        print("Network not supported")

    progMetadata = networkParser.getProgMetaData(args.urlEmission)  
    if (progMetadata["mediaType"] == "hls"):
        manifestParser = HlsManifestParser(fakeAgent=FakeAgent(), url=progMetadata["manifestUrl"], baseUrl=progMetadata["baseUrl"])
        streamData = manifestParser.getHighestResolutionStream()
        listOfSegment = manifestParser.getListOfSegment(url=streamData["URL"])

        streamDownloader = HLSStreamDownloader(fakeAgent=FakeAgent(), seglist=listOfSegment)
 
    else:
       print("Protocol not supported:%s" % progMetadata["streamType"])   


    # create the filename accoding to file meta-data
    dstFolder = tempfile.mkdtemp()
    videoFullPath = os.path.join(dstFolder, progMetadata["filename"])

    streamDownloader.download(toFile=videoFullPath, progressFnct=progressFnct)

    # convert to mp4
    if videoFullPath is not None:
        basename = os.path.splitext(os.path.basename(videoFullPath))[0]
        fname = basename + ".mp4"
        dstFullPath = os.path.join(args.outDir, fname)

        # rename file if it already exist.
        fileIndex = 2
        while os.path.isfile(dstFullPath) is True:
            dstFullPath = os.path.join(args.outDir, basename + "_" + str(fileIndex) + ".mp4")
            fileIndex += 1

        CreateMP4(videoFullPath, dstFullPath)

        # delete the
#        shutil.move(videoFullPath, os.path.join("/home", "lbr", "Dropbox", "Encoding/"))
        shutil.rmtree(dstFolder)

