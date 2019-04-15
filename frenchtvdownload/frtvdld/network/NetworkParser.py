import re
import collections

class VideoMetadata(dict):
  def __init__(self, d):
    super().__init__(d)
    self._mediaType = None
    self._manifestUrl = None
    self._airDate = None
    self._progName = None
    self._progTitle = None
    self._synopsis = None
    self._filename = None
    self._duration = None
    self._videoId = None
    self._videoUrl = None
    self._errorMsg = None

  def normalizeProgTitle(self, filename):
    s = re.sub(" - ", "-", filename)
    s = re.sub("[()':,\"]", "", s)
    s = re.sub("/", "_", s)
    s = re.sub('\s+', '_', s)
    return s

  def parseMetadata(self):
    raise NotImplementedError

  def getMetadata(self):
    self._videoUrl = self.get("videoUrl","")
    self.parseMetadata()
    Metadata = collections.namedtuple('Metadata', ['mediaType', 'manifestUrl', 'airDate', 'progName',
                                                    'progTitle', 'synopsis', 'filename', 'duration', 'videoId',
                                                     'videoUrl', "errorMsg"])
    m = Metadata(mediaType=self._mediaType, manifestUrl=self._manifestUrl, airDate=self._airDate, 
                  progName=self._progName, progTitle=self._progTitle, synopsis=self._synopsis,
                  filename=self._filename, duration=self._duration, videoId=self._videoId, 
                  videoUrl=self._videoUrl, errorMsg=self._errorMsg)
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
