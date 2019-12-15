import re
import collections
import unicodedata

class VideoMetadata(dict):
  def __init__(self, d):
    super().__init__(d)
    self._progMetadata = d
    self._mediaType = None
    self._manifestUrl = None
    self._airDate = None
    self._progCode = None
    self._networkName = None
    self._progName = None
    self._progTitle = None
    self._synopsis = None
    self._filename = None
    self._duration = None
    self._videoId = None
    self._videoUrl = None
    self._channelUrl = None
    self._errorMsg = None

  def normalizeProgTitle(self, title, default="none"):
    if not title:
      return default

    s = re.sub(" - ", "-", title)
    s = re.sub("[()':,\"]", "", s)
    s = re.sub("/", "_", s)
    s = re.sub('\s+', '_', s)
    # remove accented char
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode("utf-8")
    return s.lower()

  def parseMetadata(self):
    raise NotImplementedError()

  def getMetadata(self):
    
    self.parseMetadata()
    self._videoUrl = self.get("videoUrl","")
    self._channelUrl = self.get("channelUrl","")

    Metadata = collections.namedtuple('Metadata', ['mediaType', 'manifestUrl', 'airDate', 
                                'networkName', 'progCode', 'progName', 'progTitle', 'synopsis', 
                                'filename', 'duration', 'videoId', 'videoUrl', "channelUrl", "errorMsg", "progMetadata"])
    m = Metadata(mediaType=self._mediaType, manifestUrl=self._manifestUrl, airDate=self._airDate, 
                  networkName=self._networkName, progCode=self._progCode, progName=self._progName, 
                  progTitle=self._progTitle, synopsis=self._synopsis,
                  filename=self._filename, duration=self._duration, videoId=self._videoId, 
                  videoUrl=self._videoUrl, channelUrl=self._channelUrl, errorMsg=self._errorMsg,
                  progMetadata=self._progMetadata)
    return m


class VideoMetadataError(VideoMetadata):
  def __init__(self, url, error_msg):
    super().__init__({"videoUrl":url, "errorMsg":error_msg})

  def parseMetadata(self):
    self._errorMsg = self.get("errorMsg","Unknown error")


class NetworkParser(object):
    def __init__(self, fakeAgent):

        self.fakeAgent = fakeAgent
        self.progMetaData = {} 

    def normalizeProgTitle(self, filename):
        s = re.sub(" - ", "-", filename)
        s = re.sub("[()':,\"]", "", s)
        s = re.sub("/", "_", s)
        s = re.sub('\s+', '_', s)
        return s

    def getVideoUrl(self, url):
      raise NotImplementedError()
