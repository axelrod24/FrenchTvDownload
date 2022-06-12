import logging
import json, yaml
import time

from datetime import datetime
from datetime import date

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
    self._networkName = "arte.tv"
    data = self.get("data", {})
    data = data.get('attributes', {})

    metadata = data.get('metadata', {})
    self._progTitle = metadata.get('title', 'default_prog_title')
    self._progName = metadata.get('title', 'default_prog_name')
    self._synopsis = metadata.get('description', "no synopsis")
    self._duration = metadata.get('duration').get("seconds")

    gregorian_date = data.get('rights', {'begin': f"{date.today()}T"}).get(
        'begin').split("T", 1)[0]
    self._airDate = time.mktime(datetime.strptime(
        gregorian_date, "%Y-%m-%d").timetuple())

    self._videoId = self.get('videoId')

    streams = data.get('streams', [])
    if not len(streams):
      return

    # find the stream URL
    for s in streams:
      versions = s["versions"]
      for v in versions:
        if v["shortLabel"] in ["VF", "ST mal", "VOA", "ST mal DE"]:
          self._manifestUrl = s['url']
          self._mediaType = "hls"
          break
      if self._manifestUrl is not None:
        break

    self._filename = "%s-Arte-%s" % (datetime.fromtimestamp(
        self._airDate).strftime("%Y%m%d"), self.normalizeProgTitle(self._progTitle))


class ArteTvParser(NetworkParser):
  JSON_API = "https://api.arte.tv/api/player/v2/config/fr/_ID_EMISSION_"
  #JSON_COLLECTION_API = "https://www.arte.tv/guide/api/api/zones/fr/collection_videos?id=_ID_EMISSION_&page=_ID_PAGE_"
  #JSON_COLLECTION_API = "https://www.arte.tv/guide/api/emac/v3/fr/web/data/COLLECTION_VIDEOS/?collectionId=_ID_EMISSION_&page=_ID_PAGE_"
  JSON_COLLECTION_API = "https://www.arte.tv/api/rproxy/emac/v3/fr/web/data/COLLECTION_VIDEOS/?collectionId=_ID_EMISSION_&page=_ID_PAGE_"

  def parseCollection(self, baseUrl, nbrPage=1, nbrVideoLink=1):
    
    # read the page
    progId = self._getProgId(baseUrl)
    index = 1
    listVideoUrl=[]
    while(nbrPage==-1 or index <= nbrPage):
      url = self.JSON_COLLECTION_API.replace("_ID_EMISSION_", progId).replace("_ID_PAGE_", str(index)) 
      page = self.fakeAgent.readPage(url)
      if len(page) == 0: # nothing on the page, that's the last one.
        break
      
      jsondata = json.loads(page)
      listOfProg = jsondata.get("data", [])
      if len(listOfProg) == 0: # no list of program, end if collection
        break
      
      for prog in listOfProg:
        href = prog.get("url", "")
        if len(href) == 0:  # no link, weird but continue
          continue
        listVideoUrl.append(href)
        if len(listVideoUrl) == nbrVideoLink:
          return listVideoUrl
      
      index+=1

    return listVideoUrl


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
      raise FrTvDwnMetaDataParsingError(e)

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
      raise FrTvDwnPageParsingError(e)

