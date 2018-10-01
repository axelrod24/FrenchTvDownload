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

from FakeAgent import FakeAgent
from DownloadException import FrTvDownloadException
from GlobalRef import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class FranceTvParser(object):
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


    #  http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=166810096&catalogue=Pluzz
    # http://www.pluzz.fr/appftv/webservices/video/getInfosOeuvre.php?mode=zeri&id-diffusion=166810096
    def __init__(self, fakeAgent):

        self.fakeAgent = fakeAgent
        self.progMetaData = {} 

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
                raise (FrTvDownloadException("Can't find selected Video url"))

        logger.info("Program ID: %s" % idEmission)
        # go for JSON straight, don't even try XML
        pageInfos = self.fakeAgent.readPage(self.JSON_DESCRIPTION.replace("_ID_EMISSION_", idEmission))
        metadata = self._parseInfosJSON(pageInfos)

        #if no link to url try the other link
        if metadata['manifestUrl'] is None:
            pageInfos = self.fakeAgent.readPage(self.JSON2_DESC.replace("_ID_EMISSION_", idEmission))
            metadata = self._parseInfosJSON(pageInfos)

        # Petit message en cas de DRM
        if metadata['drm']:
            logger.warning("La vidéo posséde un DRM ; elle sera sans doute illisible")

        # Verification qu'un lien existe
        if metadata['manifestUrl'] is None:
            raise FrTvDownloadException("Aucun lien vers la vidéo")

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
            if len(videoId) == 0:
                return None

            # logger.debug("ID de l'émission : %s" % (videoId[0]["data-main-video"]))
            return videoId[0]["data-main-video"]

        except:
            raise FrTvDownloadException("Can't get or parse video ID page")

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
            raise FrTvDownloadException("Can't parse json for Francetv.fr")


class ArteTvParser(object):
    JSON_API = "https://api.arte.tv/api/player/v1/config/fr/_ID_EMISSION_"
    def __init__(self, fakeAgent):

        self.fakeAgent = fakeAgent
        self.progMetaData = {} 

    def parsePage(self, url):
        progId = self._getProgId(url)

        pageInfos = self.fakeAgent.readPage(self.JSON_API.replace("_ID_EMISSION_", progId))
        metadata = self._parseInfosJSON(pageInfos)

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
            data = data["videoJsonPlayer"]
            gregorian_date = data['VRA'].split(" ", 1)[0]
            metaData['timeStamp'] = time.mktime(datetime.datetime.strptime(gregorian_date, "%d/%m/%Y").timetuple()) 
            metaData['progName'] = data['caseProgram']
            metaData['progTitle'] = data['VTI'].replace(" : "," ").replace(", "," ").replace(":", "-").replace(" ","_").replace("/","_").replace("(",'').replace(")",'')
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
            raise FrTvDownloadException("Can't parse json for Arte.tv")


        

class NetworkProgParser(object):
    FRANCETV = 1
    ARTETV = 2
    def __init__(self, tvname):
        self._fakeAgent = FakeAgent()
        if tvname == self.FRANCETV:
            self._networkParser = FranceTvParser(self._fakeAgent)
        elif tvname == self.ARTETV:
            self._networkParser = ArteTvParser(self._fakeAgent)

    def getProgMetaData(self, url):
        self._networkParser.parsePage(url)

        return self._networkParser.progMetaData

