#!/usr/bin/env python
# -*- coding:Utf-8 -*-

import datetime
import json
import logging
import os
import re
import tempfile
import threading
import time

import BeautifulSoup
from bs4 import BeautifulSoup

from DownloadException import FrTvDownloadException
from downloader.M3U8Downloader import M3U8Downloader

logger = logging.getLogger("frtvdld")


class ArteDownloader(object):
    
    def __init__(self,
                 url,  # URL de la video
                 fakeAgent=None,  # fakeAgent to download page/file
                 stopDownloadEvent=threading.Event(),  # Event pour arreter un telechargement
                 ):

        self.fakeAgent = fakeAgent

        self.progUrl = None
        self.manifestURL = None
        self.m3u8URL = None
        self.drm = None
        self.chaine = None
        self.timeStamp = None
        self.codeProgramme = None
        self.downloader = None

        # check if url point to the video page, if not get list of video URl one by one
        videoUrl = url
        logger.info("Processing: %s" % videoUrl)
        page = self.fakeAgent.readPage(videoUrl)
        self.progUrl = self._getProgUrl(page)

        # go for JSON straight, don't even try XML
        pageInfos = self.fakeAgent.readPage(self.progUrl)
        print pageInfos
        


    def _getProgUrl(self, page):
        try:
            parsed = BeautifulSoup(page, "html.parser")
            videoUrl = parsed.find_all("iframe")
            if len(videoUrl) == 0:
                return None

            # logger.debug("Prog URL : %s" % (videoUrl[0]["src"]))
            return videoUrl[0]["src"]

        except:
            raise FrTvDownloadException("Can't get or parse video Url page")

