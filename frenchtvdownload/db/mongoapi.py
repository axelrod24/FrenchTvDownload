import datetime, json, os, logging
from db.mongomodels import Errors, Channels, Streams, Videos, Metadata


def _createMetadata(metadata):
  mdata = Metadata()
  mdata.mediaType = metadata.mediaType
  mdata.manifestUrl = metadata.manifestUrl
  mdata.airDate = datetime.datetime.fromtimestamp(metadata.airDate)
  mdata.progCode = metadata.progCode
  mdata.networkName = metadata.networkName
  mdata.progName = metadata.progName
  mdata.progTitle = metadata.progTitle
  mdata.synopsis = metadata.synopsis
  mdata.filename = metadata.filename
  mdata.duration = metadata.duration
  mdata.videoId = metadata.videoId
  mdata.videoUrl = metadata.videoUrl
  mdata.channelUrl = metadata.channelUrl
  mdata.errorMsg = metadata.errorMsg
  return mdata


def addStream(url, status="pending"):
  theStream = Streams(url = url)
  theStream.status = status
  theStream.save()
  return theStream


def updateStreamStatus(stream, status):
  stream.dateLastChecked =  datetime.datetime.utcnow
  stream.status = status
  stream.save()


def updateStreamWithError(stream, errorstring):
  error = Errors()
  error.progCode = stream.progCode
  error.networkName = stream.networkName
  error.error = errorstring

  stream.lastErrors.append(error)
  updateStreamStatus(stream, "error")


def updateStreamWithMetadata(stream, metadata, status="done"):
  # update stream with metadata
  stream.video_id = metadata.videoId
  stream.metadata = _createMetadata(metadata)
  stream.progMetadata = json.dumps(metadata.progMetadata)
  updateStreamStatus(stream, status)


def updateStreamById(video_id, metadata, status="done", progCode=None):
  # update stream with metadata
  theStream = Streams(url = metadata.videoUrl, videoId = metadata.videoId)
  theStream.networkName = metadata.networkName
  if progCode:
    theStream.progCode = progCode
  else:
    theStream.progCode = metadata.progCode

  theStream.networkName = metadata.networkName
  theStream.progMetadata = json.dumps(metadata.progMetadata)
  theStream.dateLastChecked = datetime.datetime.utcnow
  theStream.status = status
  theStream.metadata = _createMetadata(metadata)
  theStream.save()
  return theStream

def getStreamByUrl(url):
  streams = Streams.objects(url = url)
  if len(streams) == 0:
    return None

  theStream = streams[0]
  return theStream


def getStreamById(video_id):
  streams = Streams.objects(videoId = video_id)
  if len(streams) == 0:
    return None
    
  theStream = streams[0]
  return theStream

def getStreamsByStatus(status):
  streams = Streams.objects(status = status)
  return streams  


def addVideo(dstFullPath, folder, repo, progMetadata, theStream):
  theVideo = Videos(path=dstFullPath)
  theVideo.progCode = theStream.progCode
  theVideo.networkName = theStream.networkName

  theVideo.filename = progMetadata.filename
  theVideo.folder = folder
  theVideo.repo = repo
  theVideo.title = progMetadata.progName
  theVideo.duration = progMetadata.duration
  theVideo.synopsis = progMetadata.synopsis
  theVideo.firstAirDate = datetime.datetime.fromtimestamp(progMetadata.airDate)
  theVideo.stream = theStream
  theVideo.save()
  return theVideo
