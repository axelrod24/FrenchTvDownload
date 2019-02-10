import argparse
import logging
import platform
import os
import sys
import tempfile
import shutil
import dicttoxml
import threading

from frtvdld.ColorFormatter import ColorFormatter
from frtvdld.network.NetworkProgParser import networkParserFactory 
from frtvdld.downloader.HLSDownloader import HlsManifestParser, HLSStreamDownloader
from frtvdld.DownloadException import FrTvDownloadException, FrTvDwnUserInterruption

from frtvdld.FakeAgent import FakeAgent
from frtvdld.Converter import CreateMP4
from frtvdld.GlobalRef import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

def download_video(url, base_folder, progressFnct, stopDownloadEvent=threading.Event()):

    networkParser = networkParserFactory(url)
    progMetadata = networkParser.getProgMetaData()  

    # create video download specific folder
    dst_folder = os.path.join(base_folder, progMetadata["filename"])
    i=1
    while os.path.exists(dst_folder) is True:
        dst_folder = os.path.join(base_folder, progMetadata["filename"]+"_"+str(i))
        i+=1
    os.mkdir(dst_folder)

    # # generic video filename (without ext)
    # dstFullPath = os.path.join(".", progMetadata["filename"])

    # working with the manifest
    if (progMetadata["mediaType"] != "hls"):
        print("Protocol not supported:%s" % progMetadata["streamType"])
        return  

    # parse the manifest, get the highest definition and extract list of segments 
    manifestParser = HlsManifestParser(fakeAgent=FakeAgent(), url=progMetadata["manifestUrl"])
    manifestParser.parseMasterManifest()

    streamData = manifestParser.getHighestResolutionStream()
    listOfSegment = manifestParser.getListOfSegment(url=streamData["URL"])

    streamDownloader = HLSStreamDownloader(fakeAgent=FakeAgent(), seglist=listOfSegment, stopDownloadEvent=stopDownloadEvent)    

    # create the filename accoding to file meta-data
    ts_file_full_path = os.path.join(dst_folder, progMetadata["filename"]+".ts")

    try:
        streamDownloader.download(to_file=ts_file_full_path, progressFnct=progressFnct)
    except FrTvDownloadException as excepErr:
        if isinstance(excepErr, FrTvDwnUserInterruption):
            # cleanup download folder and files
            shutil.rmtree(dst_folder)
            raise FrTvDwnUserInterruption()
        else:
            raise excepErr

    # rename file if it already exist.
    mp4_file_full_path = os.path.join(dst_folder, progMetadata["filename"]+".mp4")
    i = 1
    while os.path.exists(mp4_file_full_path) is True:
        mp4_file_full_path = os.path.join(dst_folder, progMetadata["filename"]+"_"+str(i)+".mp4")
        i += 1

    CreateMP4(ts_file_full_path, mp4_file_full_path)
