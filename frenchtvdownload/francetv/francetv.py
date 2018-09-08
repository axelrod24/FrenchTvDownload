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

import BeautifulSoup
from bs4 import BeautifulSoup

from DownloadException import FrTvDownloadException
from downloader.M3U8Downloader import M3U8Downloader

logger = logging.getLogger("frenchtv")


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
    JSON_DESCRIPTION = "http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=_ID_EMISSION_&catalogue=Pluzz"
    URL_SMI = "http://www.pluzz.fr/appftv/webservices/video/getFichierSmi.php?smi=_CHAINE_/_ID_EMISSION_.smi&source=azad"
    M3U8_LINK = "http://medias2.francetv.fr/catchup-mobile/france-dom-tom/non-token/non-drm/m3u8/_FILE_NAME_.m3u8"
    REGEX_M3U8 = "/([0-9]{4}/S[0-9]{2}/J[0-9]{1}/[0-9]*-[0-9]{6,8})-"

    #  http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=166810096&catalogue=Pluzz
    # http://www.pluzz.fr/appftv/webservices/video/getInfosOeuvre.php?mode=zeri&id-diffusion=166810096
    def __init__(self,
                 url,  # URL de la video
                 fakeAgent=None,  # fakeAgent to download page/file
                 stopDownloadEvent=threading.Event(),  # Event pour arreter un telechargement
                 ):

        self.fakeAgent = fakeAgent

        # Infos video recuperees dans le XML
        self.id = None
        self.lienMMS = None
        self.lienRTMP = None
        self.manifestURL = None
        self.m3u8URL = None
        self.drm = None
        self.chaine = None
        self.timeStamp = None
        self.codeProgramme = None
        self.downloader = None

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
        self._parseInfosJSON(pageInfos)

        # Petit message en cas de DRM
        if self.drm:
            logger.warning("La vidéo posséde un DRM ; elle sera sans doute illisible")

        # Verification qu'un lien existe
        if self.m3u8URL is None:
            raise FrTvDownloadException("Aucun lien vers la vidéo")

        # create the filename accoding to file meta-data
        dstFolder = tempfile.mkdtemp()
        dstFullPath = os.path.join(dstFolder, "%s-%s.%s" % (
            datetime.datetime.fromtimestamp(self.timeStamp).strftime("%Y%m%d"), self.codeProgramme, "ts"))

        # Downloader
        self.downloader = M3U8Downloader(self.m3u8URL, dstFullPath, self.fakeAgent, stopDownloadEvent)

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
            self.lienRTMP = None
            self.lienMMS = None
            self.timeStamp = data['diffusion']['timestamp']
            self.codeProgramme = data['code_programme']
            for v in data['videos']:
                if v['format'] == 'm3u8-download':
                    self.m3u8URL = v['url']
                    self.drm = v['drm']
                elif v['format'] == 'smil-mp4':
                    self.manifestURL = v['url']
            logger.debug("URL m3u8 : %s" % (self.m3u8URL))
            logger.debug("URL manifest : %s" % (self.manifestURL))
            logger.debug("Lien RTMP : %s" % (self.lienRTMP))
            logger.debug("Lien MMS : %s" % (self.lienMMS))
            logger.debug("Utilisation de DRM : %s" % (self.drm))
        except:
            raise FrTvDownloadException("Impossible de parser le fichier JSON de l'émission")

    def download(self,
                 progressFnct=lambda x: None,  # Callback download progress
                 ):
        # delegate download to specialized downloader
        try:
            videoFile = self.downloader.download(progressFnct)
            return videoFile
        except:
            return None
