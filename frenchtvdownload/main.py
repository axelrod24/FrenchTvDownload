#!/usr/bin/python3
# # -*- coding:Utf-8 -*-

# import os
# p = os.path.abspath(os.path.dirname(__file__))
# print("Path for main:", p)

activate_this = '../.venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
print(sys.path)

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
import requests
import json

from xml.dom import minidom

from frtvdld.DownloadException import *
from frtvdld.ColorFormatter import ColorFormatter
from frtvdld.network.NetworkProgParser import networkParserFactory 
from frtvdld.downloader.HLSDownloader import HlsManifestParser, HLSStreamDownloader

from frtvdld.FakeAgent import FakeAgent
from frtvdld.Converter import CreateMP4, FfmpegHLSDownloader
from frtvdld.GlobalRef import LOGGER_NAME
#
# Main
#

REG_EXP = 'www.france.tv/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
URL_BASE = "http://localhost:5000/"
URL_PATH = "api/video"
REFERER = 'http://localhost:3000/'
ORIGIN = 'http://localhost:3000'

def post_url(url):
    service_url = os.path.join(URL_BASE, URL_PATH)
    r = requests.post(service_url, params={"url": url}, headers={"Referer": REFERER, "Origin":ORIGIN})
    if r.status_code != 200:
        logger.error("Can't access posting url service. :"+str(r.status_code))
        return

    r_status = json.loads(r.text)
    if r_status["status"] != "success":
        logger.warning("Can't post url. Error:"+r.text)
        return

    v_id = r_status["data"]["video_id"]
    service_url = os.path.join(service_url, "download")
    r = requests.get(service_url, params={"id": str(v_id)}, headers={"Referer": REFERER, "Origin":ORIGIN})
    if r.status_code != 200:
        logger.error("Can't access posting url service. :"+str(r.status_code))
        return
    logger.info(r.text)


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

    # progress function
    if (args.progressbar):
        progressFnct = lambda x: logger.info("progress : %3d%% - %d/%d" % (min(int((x[0] * 100) / x[1]), 100), x[0], x[1]))
    else:
        progressFnct = lambda x: None

    try:
        networkParser = networkParserFactory(args.urlEmission)

        # return the list of URL and exit
        if (args.parseCollection):
            url = networkParser.getVideoUrl()
            post_url(url)
            exit()

        progMetadata = networkParser.getProgMetaData()  

    except Exception as err:
        logger.error(err.__repr__())
        exit()
 
    # working with the manifest
    if (progMetadata.mediaType != "hls"):
        print("Protocol not supported:%s" % progMetadata.streamType)
        exit()

   
#     # parse the manifest, get the highest definition and extract list of segments 
#     manifestParser = HlsManifestParser(fakeAgent=FakeAgent(), url=progMetadata.manifestUrl)    
#     manifestParser.parseMasterManifest()

#     if (args.listProfiles):
#         d = manifestParser.listOfResolutions()
#         for k in d.keys():
#             print("%d:%s" % (k, d[k]))
        
#         exit(1)

#     # create the filename accoding to file meta-data
#     dstFolder = tempfile.mkdtemp()
#     videoFullPath = os.path.join(dstFolder, progMetadata.filename+".ts")

#     # downlaod the video
#     streamData = manifestParser.getHighestResolutionStream()
#     listOfSegment = manifestParser.getListOfSegment(url=streamData["URL"])
#     streamDownloader = HLSStreamDownloader(fakeAgent=FakeAgent(), seglist=listOfSegment)
#     streamDownloader.download(to_file=videoFullPath, progressFnct=progressFnct)
   
#    # write the final video files
#     if videoFullPath is not None:

#         # generic video filename (without ext)
#         dstFullPath = os.path.join(args.outDir, progMetadata.filename)

#         # rename file if it already exist.
#         fileIndex = 2
#         while os.path.isfile(dstFullPath + ".mp4") is True:
#             dstFullPath = os.path.join(args.outDir, progMetadata.filename + "_" + str(fileIndex))
#             fileIndex += 1

#         # convert to mp4
#         CreateMP4(videoFullPath, dstFullPath + ".mp4")

#         # save the metadata
#         if (args.keepMetaData):
#             xmlMeta = dicttoxml.dicttoxml(progMetadata._asdict(), attr_type=False)
#             dom = minidom.parseString(xmlMeta)
#             with open(dstFullPath+".meta", "w") as text_file:
#                 print(dom.toprettyxml(), file=text_file)

#         # save the manifest
#         if (args.keepManifest):
#             masterManifest = manifestParser.getMasterManifest()
#             with open(dstFullPath+".m3u8", "w") as text_file:
#                 print(masterManifest, file=text_file)

#         # # delete the
#         # shutil.move(videoFullPath, os.path.join("~", "Dropbox", "Encoding/"))
#         shutil.rmtree(dstFolder)

    # create the filename accoding to file meta-data
    # generic video filename (without ext)
    dstFullPath = os.path.join(args.outDir, progMetadata.filename)

    # rename file if it already exist.
    fileIndex = 2
    while os.path.isfile(dstFullPath + ".mp4") is True:
        dstFullPath = os.path.join(args.outDir, progMetadata.filename + "_" + str(fileIndex))
        fileIndex += 1

    ffmpegHLSDownloader = FfmpegHLSDownloader(url=progMetadata.manifestUrl)  
    ffmpegHLSDownloader.downlaodAndConvertFile(dst=dstFullPath)  

    