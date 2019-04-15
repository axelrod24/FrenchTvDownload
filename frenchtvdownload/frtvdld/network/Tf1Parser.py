import logging
import json, yaml
import time
import re

from datetime import datetime

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

from frtvdld.FakeAgent import FakeAgent
from frtvdld.DownloadException import *
from frtvdld.GlobalRef import LOGGER_NAME

from frtvdld.network.NetworkParser import NetworkParser, VideoMetadata

logger = logging.getLogger(LOGGER_NAME)

class Tf1VideoMetadata(VideoMetadata):
  def __init__(self, d):
    super().__init__(d)

  def parseMetadata(self):
    if self.get("code") != 200:
      raise FrTvDownloadException("Can't parse json url for Tf1")    

    self._manifestUrl = self.get('url')
    # metaData['drm'] = False
    self._mediaType = self.get("format")
    self._progTitle = self.get('media', {}).get("title", "default_prog_title")
    
    data = self.get("media",{}).get("chapters",[{}])[0]
    gregorian_date = data.get('date_diffusion')
    self._airDate = time.mktime(datetime.strptime(gregorian_date, "%Y-%m-%d").timetuple()) 
    self._synopsis = data.get("description", "no synopsis")
    self._duration = self.get('media', {}).get('duration', 0)
    self._progName = self.get('media', {}).get('owner', "default_prog_name")

    self._videoId = self.get('videoId')
    self._filename = "%s-Tf1-%s" % (datetime.fromtimestamp(self._airDate).strftime("%Y%m%d"), self.normalizeProgTitle(self._progTitle))


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
        jurl1 = self.JSON_API.replace("_ID_EMISSION_", idEmission)
        pageInfos1 = self.fakeAgent.readPage(jurl1)
        jurl2 = self.JSON_DESCRIPTION.replace("_ID_EMISSION_", idEmission)
        pageInfos2 = self.fakeAgent.readPage(jurl2)
        
        try:
          data = json.loads(pageInfos1)
          data.update(json.loads(pageInfos2))
          data["videoUrl"] = url
          data["videoId"] = jurl1
          videoMetadata = Tf1VideoMetadata(data)
          metadata = videoMetadata.getMetadata()
        except Exception as e:
          logger.error(e)
          raise FrTvDwnMetaDataParsingError()

        self.progMetaData = metadata

    def _getVideoId(self, page):
        """
        get Video ID from the video page
        """
        try:
            parsed = BeautifulSoup(page, "html.parser")
            videoId = parsed.find_all("section",
                                      attrs={"id": "content_video", "data-watid": re.compile("[0-9]+")})
            if len(videoId) == 0:
                return None

            # logger.debug("ID de l'émission : %s" % (videoId[0]["data-main-video"]))
            return videoId[0]["data-watid"]

        except Exception as e:
            logger.error(e)
            raise FrTvDwnPageParsingError()
 


