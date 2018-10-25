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
import json
import logging
import os
import re
import tempfile
import threading
import time

#import BeautifulSoup
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from FakeAgent import FakeAgent
from DownloadException import *
from GlobalRef import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

class NetworkParser(object):
    def __init__(self, fakeAgent):

        self.fakeAgent = fakeAgent
        self.progMetaData = {} 


class FranceTvParser(NetworkParser):
    """
    Parse Francetv.fr pages and extract meta-data of a given program 
    """

    DATA_MAIN_VIDEO = 'data-main-video="([0-9][a-z]-)*"'
    REGEX_ID = "http://info.francetelevisions.fr/\?id-video=([^\"]+)"
    XML_DESCRIPTION = "http://www.pluzz.fr/appftv/webservices/video/getInfosOeuvre.php?mode=zeri&id-diffusion=_ID_EMISSION_"
    URL_SMI = "http://www.pluzz.fr/appftv/webservices/video/getFichierSmi.php?smi=_CHAINE_/_ID_EMISSION_.smi&source=azad"
    M3U8_LINK = "http://medias2.francetv.fr/catchup-mobile/france-dom-tom/non-token/non-drm/m3u8/_FILE_NAME_.m3u8"
   
    REGEX_M3U8 = "/([0-9]{4}/S[0-9]{2}/J[0-9]{1}/[0-9]*-[0-9]{6,8})-"
    JSON_DESCRIPTION = "http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=_ID_EMISSION_&catalogue=Pluzz"
    JSON2_DESC="https://sivideo.webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=_ID_EMISSION_"

    def parsePage(self, url):

        # check if url point to the video page, if not get list of video URl one by one
        idEmission = None
        videoUrl = url
        i = 0
        while idEmission is None:
            logger.info("Processing: %s" % videoUrl)
            page = self.fakeAgent.readPage(videoUrl)
            idEmission = self._getVideoId(page)

            if idEmission is None:
                videoUrl = self._getListOfAvailableVideo(url, i)
                i += 1

            if videoUrl is None:
                raise FrTvDwnPageParsingError()

        logger.info("Program ID: %s" % idEmission)
        # go for JSON straight, don't even try XML
        pageInfos = self.fakeAgent.readPage(self.JSON_DESCRIPTION.replace("_ID_EMISSION_", idEmission))
        metadata = self._parseInfosJSON(pageInfos)

        #if no link to url try the other link
        if metadata['manifestUrl'] is None:
            pageInfos = self.fakeAgent.readPage(self.JSON2_DESC.replace("_ID_EMISSION_", idEmission))
            metadata = self._parseInfosJSON(pageInfos)

        metadata["videoId"] = idEmission
        # Petit message en cas de DRM
        if metadata['drm']:
            logger.warning("Video with DRM, probably can't be played")

        # Verification qu'un lien existe
        if metadata['manifestUrl'] is None:
            raise FrTvDwnManifestUrlNotFoundError()
        
        metadata["baseUrl"] = ""
        metadata["filename"] = "%s-%s.%s" % (datetime.datetime.fromtimestamp(metadata['timeStamp']).strftime("%Y%m%d"), metadata['progName'], "ts")
        self.progMetaData = metadata

    def _getVideoId(self, page):
        """
        get Video ID from the video page
        """
        # \todo LBR: process error exceptions in case page can't be loaded or videoId can't be found
        try:
            parsed = BeautifulSoup(page, "html.parser")
            videoId = parsed.find_all("div",
                                      attrs={"class": "PlayerContainer", "data-main-video": re.compile("[0-9]+")})
            # if len(videoId) == 0:
            #     return None

            # # logger.debug("ID de l'émission : %s" % (videoId[0]["data-main-video"]))
            # return videoId[0]["data-main-video"]

            # continue parsing if data-main-video
            if len(videoId) > 0:
                return videoId[0]["data-main-video"]

            videoUrlList = parsed.find_all("a", attrs={"class": "card-link", "data-link": "player",
                                                    "data-video": re.compile("[0-9]+")})

            if len(videoUrlList) > 0:
                return videoUrlList[0]["data-video"]

        except:
            raise FrTvDwnPageParsingError()

    def _getListOfAvailableVideo(self, url, index):
        page = self.fakeAgent.readPage(url)
        parsed = BeautifulSoup(page, "html.parser")
        videoUrlList = parsed.find_all("a", attrs={"class": "card-link", "data-link": "player",
                                                   "data-video": re.compile("[0-9]+")})
        if index > len(videoUrlList):
            return None

        return "https:" + videoUrlList[index]["href"]

    def _parseInfosJSON(self, pageInfos):
        """
        Parse le fichier de description JSON d'une emission
        """
        try:
            data = json.loads(pageInfos)
            metaData = {}
            metaData["mediaType"] = None
            metaData['manifestUrl'] = None
            metaData['drm'] = None
            metaData['timeStamp'] = data['diffusion']['timestamp']
            metaData['progName'] = data['code_programme']
            metaData['progTitle'] = data['sous_titre']
            metaData['synopsis'] = data['synopsis']

            # duration
            timestr = data['duree']
            metaData['duration'] = sum([a*b for a,b in zip([3600,60,1], [int(i) for i in timestr.split(":")])])

            for v in data['videos']:
                if v['format'] == 'hls_v5_os':
                    metaData['manifestUrl'] = v['url']
                    metaData['drm'] = v['drm']
                    metaData["mediaType"] = "hls"

            logger.debug("Prog name: %s" % (metaData['progName']))
            logger.debug("Prog title: %s" % (metaData['progTitle']))
            logger.debug("Stream type: %s" % (metaData['mediaType']))
            logger.debug("Manifest URL: %s" % (metaData['manifestUrl']))
            logger.debug("Drm : %s" % (metaData['drm']))
            return metaData
        except:
            raise FrTvDwnMetaDataParsingError()


class ArteTvParser(NetworkParser):
    JSON_API = "https://api.arte.tv/api/player/v1/config/fr/_ID_EMISSION_"
 
    def parsePage(self, url):
        progId = self._getProgId(url)

        pageInfos = self.fakeAgent.readPage(self.JSON_API.replace("_ID_EMISSION_", progId))
        metadata = self._parseInfosJSON(pageInfos)

        metadata["baseUrl"] = ""
        metadata["filename"] = "%s-Arte-%s.%s" % (datetime.datetime.fromtimestamp(metadata['timeStamp']).strftime("%Y%m%d"), metadata['progTitle'], "ts")
        self.progMetaData = metadata
       
    def _getProgId(self, url):
        l = url.split("/")
        i = 0
        while(i<len(l)):
            if l[i] == "videos":
                return l[i+1]
            i+=1 

        return None

    def _parseInfosJSON(self, page):
        try:
            data = json.loads(page)
            metaData = {}
            metaData["mediaType"] = None
            metaData['manifestUrl'] = None
            metaData['drm'] = None

            data = data["videoJsonPlayer"]
            if 'VRA' not in data.keys():
                return metaData
            gregorian_date = data['VRA'].split(" ", 1)[0]
            metaData['timeStamp'] = time.mktime(datetime.datetime.strptime(gregorian_date, "%d/%m/%Y").timetuple()) 
            metaData['progName'] = data['caseProgram']
            metaData['progTitle'] = data['VTI'].replace(" : "," ").replace(", "," ").replace(":", "-").replace(" ","_").replace("/","_").replace("(",'').replace(")",'')
            metaData['duration'] = data['videoDurationSeconds']
            metaData["videoId"] = data['VID']
            metaData['synopsis'] = data['VDE']

            if 'VSR' not in data.keys():
                return metaData
            
            VSR = data['VSR']
            for k in VSR:
                if not k.startswith("HLS"):
                    continue
                v = VSR[k]
                if v["versionCode"] not in ["VF-STF", "VOF-STF", "VF", "VOF"]:
                    continue

                metaData['manifestUrl'] = v['url']
                metaData['drm'] = False
                metaData["mediaType"] = "hls"
                break

            return metaData

        except:
            raise FrTvDwnMetaDataParsingError()



class Tf1Parser(NetworkParser):
    """
    Parse Tf1 pages and extract meta-data of a given program 
    """

    REGEX_M3U8 = "/([0-9]{4}/S[0-9]{2}/J[0-9]{1}/[0-9]*-[0-9]{6,8})-"
    JSON_API = "https://delivery.tf1.fr/mytf1-wrd/_ID_EMISSION_"
    JSON_DESCRIPTION = "https://www.wat.tv/interface/contentv4/_ID_EMISSION_?context=MYTF1"

    def parsePage(self, url):

        # check if url point to the video page, if not get list of video URl one by one
        idEmission = None
        videoUrl = url
        logger.info("Processing: %s" % videoUrl)
        page = self.fakeAgent.readPage(videoUrl)
        idEmission = self._getVideoId(page)

        logger.info("Program ID: %s" % idEmission)
        # go for JSON straight, don't even try XML
        pageInfos = self.fakeAgent.readPage(self.JSON_API.replace("_ID_EMISSION_", idEmission))
        metadata1 = self._parseUrlJSON(pageInfos)

        pageInfos = self.fakeAgent.readPage(self.JSON_DESCRIPTION.replace("_ID_EMISSION_", idEmission))
        metadata = self._parseInfoJSON(pageInfos)

        for k in metadata1.keys():
            metadata[k] = metadata1[k]
        
        # check that URL exist
        if metadata['manifestUrl'] is None:
            raise FrTvDownloadException("No manifest URL")

        metadata["baseUrl"] = metadata['manifestUrl'].split("%s.m3u8" % idEmission)[0]
        metadata["filename"] = "%s-Tf1-%s.%s" % (datetime.datetime.fromtimestamp(metadata['timeStamp']).strftime("%Y%m%d"), metadata['progTitle'], "ts")
        self.progMetaData = metadata

    def _getVideoId(self, page):
        """
        get Video ID from the video page
        """
        # \todo LBR: process error exceptions in case page can't be loaded or videoId can't be found
        try:
            parsed = BeautifulSoup(page, "html.parser")
            videoId = parsed.find_all("section",
                                      attrs={"id": "content_video", "data-watid": re.compile("[0-9]+")})
            if len(videoId) == 0:
                return None

            # logger.debug("ID de l'émission : %s" % (videoId[0]["data-main-video"]))
            return videoId[0]["data-watid"]

        except:
            raise FrTvDownloadException("Can't get or parse video ID page")
 
    def _parseUrlJSON(self, page):
        try:
            data = json.loads(page)
            metaData = {}
            if data["code"] != 200:
                raise FrTvDownloadException("Can't parse json url for Tf1")    
            metaData['manifestUrl'] = data['url']
            metaData['drm'] = False
            metaData["mediaType"] = data["format"]
            return metaData

        except:
            raise FrTvDownloadException("Can't parse json for Arte.tv")
 
    def _parseInfoJSON(self, page):
        try:
            data = json.loads(page)
            metaData = {}
            data = data["mediametrie"]["chapters"][0]
            metaData['progTitle'] = data['title'].split("_PLAYLISTID_")[1]
            gregorian_date = data['estatS4']
            metaData['timeStamp'] = time.mktime(datetime.datetime.strptime(gregorian_date, "%Y-%m-%d").timetuple()) 
            metaData['progName'] = ""
            return metaData

        except:
            raise FrTvDownloadException("Can't parse json for Arte.tv")


class LcpParser(NetworkParser):
    """
    Parse Tf1 pages and extract meta-data of a given program 
    """

    REGEX_M3U8 = "/([0-9]{4}/S[0-9]{2}/J[0-9]{1}/[0-9]*-[0-9]{6,8})-"
    JSON_API = "https://delivery.tf1.fr/mytf1-wrd/_ID_EMISSION_"
    JSON_DESCRIPTION = "https://www.wat.tv/interface/contentv4/_ID_EMISSION_?context=MYTF1"

    def parsePage(self, url):
        # check if url point to the video page, if not get list of video URl one by one
        videoUrl = url
        logger.info("Processing: %s" % videoUrl)

        # get and parse the page, extract metadata
        page = self.fakeAgent.readPage(videoUrl)
        parsed = BeautifulSoup(page, "html.parser")

        metaData = {}
        metaData['progTitle'] = self._getProgTitle(parsed).replace(" ", "_")
        metaData['synopsis'] = self._getSynopsis(parsed)
        metaData['timeStamp'] = self._getTimestamp(parsed)
        metaData['progName'] = ""
        metaData["filename"] = "%s-Lcp-%s.%s" % (datetime.datetime.fromtimestamp(metaData['timeStamp']).strftime("%Y%m%d"), metaData['progTitle'], "ts")

        # get the dailymotion video URL and extract manifest URL
        urlEmission = self._getVideoUrl(page)
        page = self.fakeAgent.readPage(urlEmission)

        manifestUrl = self._getManifestUrl(page)
        logger.info("manifestUrl: %s" % manifestUrl)
        metaData['manifestUrl'] = manifestUrl
        metaData['drm'] = False
        metaData["mediaType"] = "hls"
        metaData["baseUrl"] = ""

        self.progMetaData = metaData


    def _getProgTitle(self, parsed):
        try:
            meta = parsed.find_all("meta", attrs={"itemprop": "name"})
            title = meta[0]["content"] 
            return title
        except:
            raise FrTvDwnMetaDataParsingError("Can't get program title")

    def _getSynopsis(self, parsed):
        try:
            meta = parsed.find_all("meta", attrs={"name": "abstract"})
            synopsis = meta[0]["content"]
            return synopsis
        except:
            raise FrTvDwnMetaDataParsingError("Can't get program synopsis")

    def _getTimestamp(self, parsed):
        try:
            meta = parsed.find_all("span", attrs={"class": "text-muted"})
            d = meta[0].text.split(" ")
            timestamp = time.mktime(datetime.datetime.strptime(d[2], "%d/%m/%Y").timetuple()) 
            return timestamp
        except:
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

        except:
            raise FrTvDwnVideoNotFound()

    def _getManifestUrl(self, page):
        try:
            k = '"stream_chromecast_url":"'
            ib = page.find(k)
            ie = page.find('"', ib+len(k))
            manifestUrl = page[ib+len(k):ie].replace("\\","")
            return manifestUrl 
        except:
            raise FrTvDwnManifestUrlNotFoundError()


class NetworkProgParser(object):
    FRANCETV = 1
    ARTETV = 2
    TF1 = 3 
    LCP = 4

    def __init__(self, tvname):
        self._fakeAgent = FakeAgent()
        if tvname == self.FRANCETV:
            self._networkParser = FranceTvParser(self._fakeAgent)
        elif tvname == self.ARTETV:
            self._networkParser = ArteTvParser(self._fakeAgent)
        elif tvname == self.TF1:
            self._networkParser = Tf1Parser(self._fakeAgent)
        elif tvname == self.LCP:
            self._networkParser = LcpParser(self._fakeAgent)

    def getProgMetaData(self, url):
        self._networkParser.parsePage(url)

        return self._networkParser.progMetaData


def getVideoMetadata(prog_url):
    logger.info(prog_url)
    parsed_uri = urlparse(prog_url)

    if parsed_uri.netloc == "www.france.tv" or parsed_uri.netloc == "france.tv":
        networkParser = NetworkProgParser(NetworkProgParser.FRANCETV)
    elif parsed_uri.netloc == "www.arte.tv" or parsed_uri.netloc == "arte.tv":
        networkParser = NetworkProgParser(NetworkProgParser.ARTETV)
    elif parsed_uri.netloc == "www.tf1.fr" or parsed_uri.netloc == "tf1.fr":
        networkParser = NetworkProgParser(NetworkProgParser.TF1)
    elif parsed_uri.netloc == "www.lcp.fr" or parsed_uri.netloc == "lcp.fr":
        networkParser = NetworkProgParser(NetworkProgParser.LCP)
    else:
        print("Network not supported")

    progMetadata = networkParser.getProgMetaData(prog_url)  
    return progMetadata
