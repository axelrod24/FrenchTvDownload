import logging
import json, yaml
import time

from datetime import datetime

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

from frtvdld.FakeAgent import FakeAgent
from frtvdld.DownloadException import *
from frtvdld.GlobalRef import LOGGER_NAME

from frtvdld.network.NetworkParser import NetworkParser, VideoMetadata

logger = logging.getLogger(LOGGER_NAME)

class ArteTvVideoMetadata(VideoMetadata):
  def __init__(self, d):
    super().__init__(d)

  def parseMetadata(self):
    data = self.get("videoJsonPlayer", {})
    if 'VRA' not in data.keys():
        data = {}

    gregorian_date = data['VRA'].split(" ", 1)[0]
    self._airDate = time.mktime(datetime.strptime(gregorian_date, "%d/%m/%Y").timetuple()) 
    self._progName = data.get('caseProgram', 'default_prog_name')
    self._progTitle = data.get('VTI', 'default_prog_title')
    self._duration = data.get('videoDurationSeconds', 0)
    self._synopsis = data.get('VDE', "no synopsis")
    
    self._videoId = self.get('videoId')
    
    if 'VSR' not in data.keys():
        return
    
    VSR = data['VSR']
    for k in VSR:
        if not k.startswith("HLS"):
            continue
        v = VSR[k]
        if v["versionCode"] not in ["VF-STF", "VOF-STF", "VF", "VOF", "VO-STF"]:
            continue

        self._manifestUrl = v['url']
        # metaData['drm'] = False
        self._mediaType = "hls"
        break

    self._filename = "%s-Arte-%s" % (datetime.fromtimestamp(self._airDate).strftime("%Y%m%d"), self.normalizeProgTitle(self._progTitle))


class ArteTvParser(NetworkParser):
    JSON_API = "https://api.arte.tv/api/player/v1/config/fr/_ID_EMISSION_"
    JSON_COLLECTION_API = "https://www.arte.tv/guide/api/api/zones/fr/collection_videos?id=_ID_EMISSION_&page=_ID_PAGE_"

    def getListOfUrlCollection(self, url):

        progId = self._getProgId(url)

        # not a collection ID
        if not progId.startswith("RC-"):
            return None

        allUrl = []
        jurl = self.JSON_COLLECTION_API.replace("_ID_EMISSION_", progId)
        pageId = 1
        while True:
            jurlTemp = jurl.replace("_ID_PAGE_", str(pageId))
            pageInfo = self.fakeAgent.readPage(jurlTemp)
            if not self._getCollectionUrls(pageInfo, allUrl):
                break

            pageId += 1

        return allUrl

    def parsePage(self, url):
        progId = self._getProgId(url)

        jurl = self.JSON_API.replace("_ID_EMISSION_", progId)
        pageInfos = self.fakeAgent.readPage(jurl)
        # parse Metadata
        try:
          data = json.loads(pageInfos)
          data["videoUrl"] = url
          data["videoId"] = jurl
          videoMetadata = ArteTvVideoMetadata(data)
          metadata = videoMetadata.getMetadata()
        except Exception as e:
          logger.error(e)
          raise FrTvDwnMetaDataParsingError()

        self.progMetaData = metadata
       
    def _getProgId(self, url):
        try:
            l = url.split("/")
            i = 0
            while(i<len(l)):
                if l[i] == "videos":
                    return l[i+1]
                i+=1 

            return None
            
        except Exception as e:
            logger.error(e)
            raise FrTvDwnPageParsingError()

    def _getCollectionUrls(self, pageInfo, allUrl):
        pass
           

