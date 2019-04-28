#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# Notes :
#	 -> Filtre Wireshark :
#		   http.host contains "ftvodhdsecz" or http.host contains "francetv" or http.host contains "pluzz"
#	 ->

#
# Modules
#

import datetime
import json, yaml
import logging
import os
import re
import tempfile
import threading
import time

#import BeautifulSoup
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

from frtvdld.FakeAgent import FakeAgent
from frtvdld.DownloadException import *
from frtvdld.GlobalRef import LOGGER_NAME

from frtvdld.network.NetworkParser import NetworkParser, VideoMetadataError
from frtvdld.network.FranceTvParser import FranceTvParser
from frtvdld.network.ArteTvParser import ArteTvParser
from frtvdld.network.Tf1Parser import Tf1Parser

logger = logging.getLogger(LOGGER_NAME)


class LcpParser(NetworkParser):
    """
    Parse LCP pages and extract meta-data of a given program 
    """

    def parsePage(self, url):
        # check if url point to the video page, if not get list of video URl one by one
        videoUrl = url
        logger.info("Processing: %s" % videoUrl)

        # get and parse the page, extract metadata
        page = self.fakeAgent.readPage(videoUrl)
        parsed = BeautifulSoup(page, "html.parser")

        metaData = {}
        metaData['progTitle'] = self._getProgTitle(parsed)
        metaData['synopsis'] = self._getSynopsis(parsed)
        metaData['timeStamp'] = self._getTimestamp(parsed)
        metaData['progName'] = ""
        metaData["filename"] = "%s-Lcp-%s" % (datetime.datetime.fromtimestamp(metaData['timeStamp']).strftime("%Y%m%d"), self.normalizeProgTitle(metaData['progTitle']))

        # get the dailymotion video URL and extract manifest URL
        urlEmission = self._getVideoUrl(page)
        page = self.fakeAgent.readPage(urlEmission)
        metaData["videoId"] = urlEmission

        manifestUrl = self._getManifestUrl(page)
        logger.info("manifestUrl: %s" % manifestUrl)
        metaData['manifestUrl'] = manifestUrl
        metaData['drm'] = False
        metaData["mediaType"] = "hls"

        self.progMetaData = metaData


    def _getProgTitle(self, parsed):
        try:
            meta = parsed.find_all("meta", attrs={"itemprop": "name"})
            title = meta[0]["content"] 
            return title

        except Exception as e:
            logger.error(e)
            raise FrTvDwnMetaDataParsingError("Can't get program title")

    def _getSynopsis(self, parsed):
        try:
            meta = parsed.find_all("meta", attrs={"name": "abstract"})
            synopsis = meta[0]["content"]
            return synopsis

        except Exception as e:
            logger.error(e)
            raise FrTvDwnMetaDataParsingError("Can't get program synopsis")

    def _getTimestamp(self, parsed):
        try:
            meta = parsed.find_all("span", attrs={"class": "text-muted"})
            d = meta[0].text.split(" ")
            timestamp = time.mktime(datetime.datetime.strptime(d[2], "%d/%m/%Y").timetuple()) 
            return timestamp

        except Exception as e:
            logger.error(e)
            raise FrTvDwnMetaDataParsingError("Can't get program timestamp")

    def _getVideoUrl(self, page):
       # \todo LBR: process error exceptions in case page can't be loaded or videoId can't be found
        try:
            parsed = BeautifulSoup(page, "html.parser")
            iFrame = parsed.find_all("iframe",
                                      attrs={"class": "embed-responsive-item"})

            # logger.debug("ID de l'émission : %s" % (videoId[0]["data-main-video"]))
            url = iFrame[0]["src"]
            purl = urlparse(url)
            nurl = purl._replace(scheme="https")
            return nurl.geturl()

        except Exception as e:
            logger.error(e)
            raise FrTvDwnVideoNotFound()

    def _getManifestUrl(self, page):
        try:
            k = '"stream_chromecast_url":"'
            ib = page.find(k)
            ie = page.find('"', ib+len(k))
            manifestUrl = page[ib+len(k):ie].replace("\\","")
            return manifestUrl 

        except Exception as e:
            logger.error(e)
            raise FrTvDwnManifestUrlNotFoundError()


class NetworkProgParser(object):
    FRANCETV = 1
    ARTETV = 2
    TF1 = 3 
    LCP = 4

    def __init__(self, tvname, url):
        self._fakeAgent = FakeAgent()
        self._url = url

        if tvname == self.FRANCETV:
            self._networkParser = FranceTvParser(self._fakeAgent)
        elif tvname == self.ARTETV:
            self._networkParser = ArteTvParser(self._fakeAgent)
        elif tvname == self.TF1:
            self._networkParser = Tf1Parser(self._fakeAgent)
        # no allowing LCP right now ...
        # elif tvname == self.LCP:
        #     self._networkParser = LcpParser(self._fakeAgent)

    def getProgMetaData(self):
        self._networkParser.parsePage(self._url)
        return self._networkParser.progMetaData

    def getVideoUrl(self):
        listOfUrl = self._networkParser.getVideoUrl(self._url)
        return listOfUrl


def networkParserFactory(progUrl):
    logger.info(progUrl)
    parsed_uri = urlparse(progUrl)

    if parsed_uri.netloc == "www.france.tv" or parsed_uri.netloc == "france.tv":
        networkParser = NetworkProgParser(NetworkProgParser.FRANCETV, progUrl)
    elif parsed_uri.netloc == "www.arte.tv" or parsed_uri.netloc == "arte.tv":
        networkParser = NetworkProgParser(NetworkProgParser.ARTETV, progUrl)
    elif parsed_uri.netloc == "www.tf1.fr" or parsed_uri.netloc == "tf1.fr":
        networkParser = NetworkProgParser(NetworkProgParser.TF1, progUrl)
    elif parsed_uri.netloc == "www.lcp.fr" or parsed_uri.netloc == "lcp.fr":
        networkParser = NetworkProgParser(NetworkProgParser.LCP, progUrl)
    else:
        print("Network not supported")
        return None

    return networkParser
