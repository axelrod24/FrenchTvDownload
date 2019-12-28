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
    deliveryTag = self.get('delivery', {})
    if deliveryTag.get("code") != 200:
      raise FrTvDownloadException("Can't parse json url for Tf1")    

    self._manifestUrl = deliveryTag.get('url')
    self._mediaType = deliveryTag.get("format")

    self._progTitle = self.get('content', {}).get("title", "default_prog_title")
    self._progName = self.get('media', {}).get('owner', "default_prog_name")
    self._duration = self.get('media', {}).get('duration', 0)

    data = self.get("mediametrie",{}).get("chapters",[{}])[0]
    gregorian_date = data.get('estatS4')
    self._airDate = time.mktime(datetime.strptime(gregorian_date, "%Y-%m-%d").timetuple()) 
    self._synopsis = "%s\r\n%s" % (self.get('media', {}).get('title', ""), self.get('synopsis'))

    self._videoId = self.get('videoId')
    self._filename = "%s-Tf1-%s" % (datetime.fromtimestamp(self._airDate).strftime("%Y%m%d"), self.normalizeProgTitle(self._progTitle))


class Tf1Parser(NetworkParser):
    """
    Parse Tf1 pages and extract meta-data of a given program 
    """

    REGEX_M3U8 = "/([0-9]{4}/S[0-9]{2}/J[0-9]{1}/[0-9]*-[0-9]{6,8})-"
    JSON_API = "https://delivery.tf1.fr/mytf1-wrd/_ID_EMISSION_"
    JSON_DESCRIPTION = "https://www.wat.tv/interface/contentv4/_ID_EMISSION_?context=MYTF1"
    JSON_API = "https://player.tf1.fr/mediainfocombo/_ID_EMISSION_?context=MYTF1&pver=4001000"

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
        # jurl2 = self.JSON_DESCRIPTION.replace("_ID_EMISSION_", idEmission)
        # pageInfos2 = self.fakeAgent.readPage(jurl2)
        
        try:
          data = json.loads(pageInfos1)
          # data.update(json.loads(pageInfos2))
          data["videoUrl"] = url
          data["videoId"] = idEmission
          data["synopsis"] = self._getSynopsis(page)

          videoMetadata = Tf1VideoMetadata(data)
          metadata = videoMetadata.getMetadata()
        except Exception as e:
          logger.error(e)
          raise FrTvDwnMetaDataParsingError(e)

        self.progMetaData = metadata

    def _findProgPageMetadata(self, page):
      try:
        parsed = BeautifulSoup(page, "html.parser")
        scripts = parsed.find_all("script")
        if len(scripts) == 0:
            return None

        for script in scripts:
          # extract stream id for var definition
          if script.text.startswith("window.__APOLLO_STATE__"):
            return script
        
        return None

      except Exception as e:
        logger.error(e)
        raise FrTvDwnPageParsingError(e)

    def _getVideoId(self, page):
      """
      get Video ID from the video page
      """
      try:
        script = self._findProgPageMetadata(page)
        sindex = script.text.find('"streamId":')
        eindex = sindex + script.text[sindex:].find(',')
        val = script.text[sindex:eindex]
        vid = val.split(':')[1].strip("'\" ")
        return vid

      except Exception as e:
        logger.error(e)
        raise FrTvDwnPageParsingError(e)

    def _getSynopsis(self, page):
      try:
        script = self._findProgPageMetadata(page)
        sindex = script.text.find('"__typename":"Decoration"')
        sindex = sindex + script.text[sindex:].find(',')
        sindex = sindex + script.text[sindex:].find(':')
        sindex = sindex + script.text[sindex:].find('"')
        sindex+=1
        eindex = sindex + script.text[sindex:].find('"')

        val = script.text[sindex:eindex]
        val = val.strip("'\" ")
        return val
          
      except Exception as e:
        logger.error(e)
        raise FrTvDwnPageParsingError(e)

      parsed = BeautifulSoup(page, "html.parser")
      desc = parsed.find_all("meta", attrs={"property": "og:description"})
      if len(desc) > 0:
        return desc[0].attrs["content"]
      return "no_synopsis"
 


