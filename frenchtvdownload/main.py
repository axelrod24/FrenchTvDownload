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
import dicttoxml

from xml.dom.minidom import parseString

from frtvdld.DownloadException import *
from frtvdld.ColorFormatter import ColorFormatter
from frtvdld.network.NetworkProgParser import networkParserFactory 
from frtvdld.downloader.HLSDownloader import HlsManifestParser, HLSStreamDownloader

from frtvdld.FakeAgent import FakeAgent
from frtvdld.Converter import CreateMP4
from frtvdld.GlobalRef import LOGGER_NAME
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

    parser.add_argument("--keepManifest", action='store_true', default=False, help="save the master HLS manifest (.m3u8)")
    parser.add_argument("--keepMetaData", action='store_true', default=False, help="save the video metadata (.meta)")
    parser.add_argument("--listProfiles", action='store_true', default=False, help="return list of available resolution (don't download the video)")
    parser.add_argument("--parseCollection", action='store_true', default=False, help="return a list of video URL which are part of a collection")

    parser.add_argument("--nocolor", action='store_true', default=False, help='turn of color in terminal')
    parser.add_argument("--version", action='version', version="FrenchTvDownloader %s" % (__version__))
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

    try:

        networkParser = networkParserFactory(args.urlEmission)

        # return the list of URL and exit
        if (args.parseCollection):
            listOfUrl = networkParser.getListOfUrlCollection()
            for u in listOfUrl:
                print(u)
            
            exit(1)
        
        progMetadata = networkParser.getProgMetaData()  

    except FrTvDownloadException as excepErr:
        if isinstance(excepErr, FrTvDwnVideoNotFound):
            error = "Can't find video: %s" % args.urlEmission
        elif isinstance(excepErr, FrTvDwnPageParsingError):
            error = "Can't get or parse video ID page: %s" % args.urlEmission
        elif isinstance(excepErr, FrTvDwnManifestUrlNotFoundError):
            error = "Can't parse video metadata: %s" % args.urlEmission
        elif isinstance(excepErr, FrTvDwnMetaDataParsingError):
            error = "Can't get manifest URL: %s" % args.urlEmission
        else:
            error = "Unknown error getting metadata for %s" % args.urlEmission

        logger.error(error)
        exit()
 
    # generic video filename (without ext)
    dstFullPath = os.path.join(args.outDir, progMetadata["filename"])

    # save the metadata
    if (args.keepMetaData):
        xmlMeta = dicttoxml.dicttoxml(progMetadata, attr_type=False)
        dom = parseString(xmlMeta)
        with open(dstFullPath+".meta", "w") as text_file:
            print(dom.toprettyxml(), file=text_file)

    # working with the manifest
    if (progMetadata["mediaType"] == "hls"):
        manifestParser = HlsManifestParser(fakeAgent=FakeAgent(), url=progMetadata["manifestUrl"])
        
        # save the manifest
        if (args.keepManifest):
            masterManifest = manifestParser.getMasterManifest()
            with open(dstFullPath+".m3u8", "w") as text_file:
                print(masterManifest, file=text_file)

        # parse the manifest, get the highest definition and extract list of segments 
        manifestParser.parseMasterManifest()

        if (args.listProfiles):
            d = manifestParser.listOfResolutions()
            for k in d.keys():
                print("%d:%s" % (k, d[k]))
            
            exit(1)

        streamData = manifestParser.getHighestResolutionStream()
        listOfSegment = manifestParser.getListOfSegment(url=streamData["URL"])

        streamDownloader = HLSStreamDownloader(fakeAgent=FakeAgent(), seglist=listOfSegment)
 
    else:
       print("Protocol not supported:%s" % progMetadata["streamType"])   


    # create the filename accoding to file meta-data
    dstFolder = tempfile.mkdtemp()
    videoFullPath = os.path.join(dstFolder, progMetadata["filename"]+".ts")

    streamDownloader.download(to_file=videoFullPath, progressFnct=progressFnct)

    # convert to mp4
    if videoFullPath is not None:

        # rename file if it already exist.
        fileIndex = 2
        while os.path.isfile(dstFullPath + ".mp4") is True:
            dstFullPath = os.path.join(args.outDir, progMetadata["filename"] + "_" + str(fileIndex))
            fileIndex += 1

        CreateMP4(videoFullPath, dstFullPath + ".mp4")

        # # delete the
        # shutil.move(videoFullPath, os.path.join("~", "Dropbox", "Encoding/"))
        shutil.rmtree(dstFolder)

