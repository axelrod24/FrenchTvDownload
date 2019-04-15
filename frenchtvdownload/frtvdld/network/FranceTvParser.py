import logging
import json, yaml

from datetime import datetime

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
    self._airDate = self.get('diffusion')['timestamp']  #\TODO LBR: add default date value
    self._progName = self.get('code_programme', 'default_prog_name')
    self._progTitle = self.get('sous_titre', 'default_prog_title')
    self._synopsis = self.get('synopsis', "no synopsis")
    self._videoId = self.get('videoId')

    # duration (default value to 0 if not present)
    timestr = self.get('duree', '0:0:0')
    self._duration = sum([a*b for a,b in zip([3600,60,1], [int(i) for i in timestr.split(":")])])

    for v in self.get('videos'):
        if v.get('format') == 'hls_v5_os':
            self._manifestUrl = v.get('url')
            # metaData['drm'] = v['drm']
            self._mediaType = "hls"

    self._filename = "%s-%s" % (datetime.fromtimestamp(self._airDate).strftime("%Y%m%d"), self.normalizeProgTitle(self._progName))


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
    JSON3_DESC="https://player.webservices.francetelevisions.fr/v1/videos/_ID_EMISSION_?country_code=FR&w=1920&h=1080&version=5.5.2&domain=www.france.tv&device_type=desktop&browser=chrome&browser_version=71&os=macos&os_version=10_13_6"

    def getListOfUrlCollection(self, url):
        # read the page and extract list of videoURL
        page = self.fakeAgent.readPage(url)
        allUrl = self._getVideoId(page, getAllUrl=True)

        # sort out valid video URL based on baseUrl path
        baseUrlPath = urlparse(url).path
        urlList = []
        for u in allUrl:
            uPath = urlparse(u).path
            if (uPath.startswith(baseUrlPath)):
                urlList.append(u)

        return urlList

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
        jurl = self.JSON_DESCRIPTION.replace("_ID_EMISSION_", idEmission)
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
            div_tag = parsed.find_all("div", class_="c-player-content")
            if len(div_tag) == 0:
                return None

            script_tag = div_tag[0].find_all("script")
            if len(script_tag) == 0:
                return None

            # assume script is the first element of the array
            script_tag = script_tag[0]
            json_text = script_tag.text
            json_text = json_text[json_text.find("["):json_text.rfind("]")+1]

            data = yaml.load(json_text)

            data = data[0]
            return data["videoId"]

        except Exception as e:
            logger.error(e)
            raise FrTvDwnPageParsingError(e)

    def _getListOfAvailableVideo(self, url, index):
        page = self.fakeAgent.readPage(url)
        parsed = BeautifulSoup(page, "html.parser")
        videoUrlList = parsed.find_all("a", attrs={"class": "c-card-video__link"})

        if index > len(videoUrlList):
            return None

        return urljoin(url, videoUrlList[index]["href"])
  