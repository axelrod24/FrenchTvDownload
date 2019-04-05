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

  def normalizeProgTitle(self, filename):
    s = re.sub(" - ", "-", filename)
    s = re.sub("[()':,\"]", "", s)
    s = re.sub("/", "_", s)
    s = re.sub('\s+', '_', s)
    return s

  def parseMetadata(self):
    raise NotImplementedError

  def getMetadata(self):
    self.parseMetadata()
    Metadata = collections.namedtuple('Metadata', ['mediaType', 'manifestUrl', 'airDate', 'progName',
                                                    'progTitle', 'synopsis', 'filename', 'duration', 'videoId'])
    m = Metadata(mediaType=self._mediaType, manifestUrl=self._manifestUrl, airDate=self._airDate, 
                  progName=self._progName, progTitle=self._progTitle, synopsis=self._synopsis,
                  filename=self._filename, duration=self._duration, videoId=self._videoId)
    return m


  

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
