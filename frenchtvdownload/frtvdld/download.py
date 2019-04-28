import argparse
import logging
import platform
import os
import sys
import tempfile
import shutil
import threading

from frtvdld.ColorFormatter import ColorFormatter
from frtvdld.network.NetworkProgParser import networkParserFactory, VideoMetadataError
from frtvdld.downloader.HLSDownloader import HlsManifestParser, HLSStreamDownloader
from frtvdld.DownloadException import *

from frtvdld.FakeAgent import FakeAgent
from frtvdld.GlobalRef import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

def get_error_metadata(url, error_msg):
    metadata = VideoMetadataError(url, error_msg)
    return metadata

def get_video_metadata(url):
    networkParser = networkParserFactory(url)
    progMetadata = networkParser.getProgMetaData()  
    return progMetadata


def download_video(manifestUrl, filename, progressFnct, stopDownloadEvent=threading.Event()):

    try:
        # parse the manifest, get the highest definition and extract list of segments 
        manifestParser = HlsManifestParser(fakeAgent=FakeAgent(), url=manifestUrl)
        manifestParser.parseMasterManifest()

        streamData = manifestParser.getHighestResolutionStream()
        listOfSegment = manifestParser.getListOfSegment(url=streamData["URL"])
    except Exception as err:
        raise FrTvDwnManifestError(err.__repr__())

    try:
        streamDownloader = HLSStreamDownloader(fakeAgent=FakeAgent(), seglist=listOfSegment, stopDownloadEvent=stopDownloadEvent)    
        streamDownloader.download(to_file=filename, progressFnct=progressFnct)
    except Exception as err:
        if isinstance(err, FrTvDwnUserInterruption):
            raise err

        raise FrTvDwnSegmentError(err.__repr__())
