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

from DownloadException import FrTvDownloadException
from GlobalRef import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


#
# Classes
#

class FranceTvDownloader(object):
    """
    Classe principale pour lancer un telechargement
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
    def __init__(self,
                 url,  # URL de la video
                 fakeAgent=None,  # fakeAgent to download page/file
                 stopDownloadEvent=threading.Event(),  # Event pour arreter un telechargement
                 ):

        self.fakeAgent = fakeAgent
        self.progMetaData = {} 

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

        # # create the filename accoding to file meta-data
        # dstFolder = tempfile.mkdtemp()
        # dstFullPath = os.path.join(dstFolder, metadata["filename"])

        # # Downloader
        # self.downloader = M3U8Downloader(asset['manifestUrl'], dstFullPath, self.fakeAgent, stopDownloadEvent)

    def getProgMetaData(self):
        return self.progMetaData

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
            metaData["streamType"] = None
            metaData['manifestUrl'] = None
            metaData['drm'] = None
            metaData['timeStamp'] = data['diffusion']['timestamp']
            metaData['progName'] = data['code_programme']
            metaData['progTitle'] = data['sous_titre']
            for v in data['videos']:
                if v['format'] == 'hls_v5_os':
                    metaData['manifestUrl'] = v['url']
                    metaData['drm'] = v['drm']
                    metaData["streamType"] = "hls"

            logger.debug("Prog name: %s" % (metaData['progName']))
            logger.debug("Prog title: %s" % (metaData['progTitle']))
            logger.debug("Stream type: %s" % (metaData['streamType']))
            logger.debug("Manifest URL: %s" % (metaData['manifestUrl']))
            logger.debug("Drm : %s" % (metaData['drm']))
            return metaData
        except:
            raise FrTvDownloadException("Impossible de parser le fichier JSON de l'émission")

    def download(self,
                 progressFnct=lambda x: None,  # Callback download progress
                 ):
        # delegate download to specialized downloader
        try:
            videoFile = self.downloader.download(progressFnct)
            return videoFile
        except ValueError as err:
            print("Error:{0}".format(err))
            return None
