import datetime, json, os, logging
from db.mongomodels import Errors, Channels, Streams, Videos


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
  theStream.save()
  return theStream


def getStreamById(video_id):
  streams = Streams.objects(videoId = video_id)
  if len(streams) == 0:
    return None
    
  theStream = streams[0]
  return theStream


def addVideo(dstFullPath, folder, repo, progMetadata, theStream):
  theVideo = Videos(path=dstFullPath)
  theVideo.progCode = progMetadata.progCode
  theVideo.networkName = progMetadata.networkName
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
