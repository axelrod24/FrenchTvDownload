import logging
import json, yaml

from datetime import datetime
try:
    from backports.datetime_fromisoformat import MonkeyPatch
    MonkeyPatch.patch_fromisoformat()
except ModuleNotFoundError:
    pass
    # ignore error if this package can't be found
    
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

from frtvdld.FakeAgent import FakeAgent
from frtvdld.DownloadException import *
from frtvdld.GlobalRef import LOGGER_NAME

from frtvdld.network.NetworkParser import NetworkParser, VideoMetadata

logger = logging.getLogger(LOGGER_NAME)


class FranceTvVideoMetadata(VideoMetadata):
  def __init__(self, d):
    super().__init__(d)

  def parseMetadata(self):

    self._networkName="france.tv"
    self._manifestUrl = self.get('manifest')
    self._synopsis = self.get('synopsis', "no_synopsis")
    
    vMeta =  self.get('video')
    #self._manifestUrl = vMeta.get('url')
    self._mediaType = vMeta.get('format') 
    self._duration = vMeta.get('duration') 
    
    pMeta = self.get('meta')
    self._videoId = pMeta.get('id')

    pName = pMeta.get('title', 'default_prog_name')
    self._progName = self.normalizeProgTitle(pName, 'default_prog_name')

    pTitle = pMeta.get('additional_title', 'default_prog_title')
    self._progTitle = self.normalizeProgTitle(pTitle, 'default_prog_title')

    self._airDate = self._parseAirDate(pMeta.get('broadcasted_at'))  #\TODO LBR: add default date value

    self._filename = "%s-%s" % (datetime.fromtimestamp(self._airDate).strftime("%Y%m%d"), self.normalizeProgTitle(self._progName))
  
  def _parseAirDate(self, str_date):
    split_date = str_date.split("T")[0]
    d = datetime.fromisoformat(split_date)
    return d.timestamp()


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
    JSON_DESCRIPTION = "http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=_ID_EMISSION_"
    JSON2_DESC="https://sivideo.webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=_ID_EMISSION_"
    JSON3_DESC="https://player.webservices.francetelevisions.fr/v1/videos/_ID_EMISSION_?country_code=FR&w=1920&h=1080&device_type=desktop&browser=safari"

    REPLAY_VIDEO_URL = "%s/toutes-les-videos/?page=%d"

    def parseCollection(self, baseUrl, nbrPage=1, nbrVideoLink=1):
      index = 0
      # read the page
      listVideoUrl=[]
      while(nbrPage==-1 or index < nbrPage):
        url = self.REPLAY_VIDEO_URL % (baseUrl.rstrip('/'), index) 
        page = self.fakeAgent.readPage(url)
        if len(page)==0: # nothing on the page, that's the last one.
          break
        parsed = BeautifulSoup(page, "html.parser")
        cardVideos = parsed.find_all("div", attrs={"class": "c-card-video"})
        for card in cardVideos:
          s = card.find_all("span", attrs={"class": "c-label"})
          if len(s) > 0:  # ignore "extrait"
            if s[0].text == "extrait":
              continue
          href = card.find_all("a", attrs={"class": "c-card-video__textarea-link"})
          if len(href) == 0:  # no link, weird but continue
            continue

          videoUrl = urljoin(baseUrl, href[0]["href"])
          listVideoUrl.append(videoUrl)
          if len(listVideoUrl) == nbrVideoLink:
            return listVideoUrl

        index+=1

      return listVideoUrl


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
              raise FrTvDwnPageParsingError("No valid video link")

        logger.info("Program ID: %s" % idEmission)

        # go for JSON straight, don't even try XML
        # jurl = self.JSON_DESCRIPTION.replace("_ID_EMISSION_", idEmission)
        jurl = self.JSON3_DESC.replace("_ID_EMISSION_", idEmission)
        pageInfos = self.fakeAgent.readPage(jurl)
        
        # parse Metadata
        try:
          data = json.loads(pageInfos)
          data["synopsis"] = self._getSynopsis(page)
          data["videoUrl"] = videoUrl
          data["channelUrl"] = url
          data["videoId"] = jurl

          # fetch token url
          tokenUrl = data.get("video", {"token": None}).get("token")
          if (tokenUrl):
            url = self._fetchTokenUrl(tokenUrl)
            if not url:
              raise FrTvDwnPageParsingError("Error fetching tokenUrl")

            data['manifest'] = url
          else:
            data['manifest'] = data.get("video", {"url": None}).get('url')

          videoMetadata = FranceTvVideoMetadata(data)
          metadata = videoMetadata.getMetadata()
        except Exception as e:
          logger.error(e)
          raise FrTvDwnMetaDataParsingError(e)

        #if no link to url try the other link
        if metadata.manifestUrl is None:
            jurl = self.JSON2_DESC.replace("_ID_EMISSION_", idEmission)
            pageInfos = self.fakeAgent.readPage(jurl)
             # parse Metadata
            try:
              data = json.loads(pageInfos)
              data["videoUrl"] = url
              data["videoId"] = jurl
              videoMetadata = FranceTvVideoMetadata(data)
              
              metadata = videoMetadata.getMetadata()
            except Exception as e:
                logger.error(e)
                raise FrTvDwnMetaDataParsingError(e)

        self.progMetaData = metadata

    def _getVideoId(self, page, getAllUrl=False):
        """
        get Video ID from the video page
        """
        try:
            parsed = BeautifulSoup(page, "html.parser")
            div_tag = parsed.find_all("div", class_="c-player")
            if len(div_tag) == 0:
                return None

            script_tag = div_tag[0].nextSibling
            if script_tag.name !=  "script":
                return None

            # extract Video Id from script text
            json_text = script_tag.text
            json_text = json_text[json_text.find("["):json_text.rfind("]")+1]

            # replace wrong escape character .... 
            json_text = json_text.replace("\\/","/")

            data = yaml.load(json_text)
            data = data[0]
            return data["videoId"]

        except Exception as e:
            logger.error(e)
            raise FrTvDwnPageParsingError(e)

    def _getListOfAvailableVideo(self, url, index):
        page = self.fakeAgent.readPage(url)
        parsed = BeautifulSoup(page, "html.parser")
        videoUrlList = parsed.find_all("a", attrs={"class": "c-card-video__textarea-link"})

        if index >= len(videoUrlList):
            return None

        return urljoin(url, videoUrlList[index]["href"])

    def _fetchTokenUrl(self, url):
      page = self.fakeAgent.readPage(url)
      data = json.loads(page)
      return data.get('url')
    
    def _getSynopsis(self, page):
      parsed = BeautifulSoup(page, "html.parser")
      desc = parsed.find_all("meta", attrs={"property": "og:description"})
      if len(desc) > 0:
        return desc[0].attrs["content"]
      return "no_synopsis"
