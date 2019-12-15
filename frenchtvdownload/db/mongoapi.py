import datetime, json, os, logging
from db.mongomodels import Errors, Channels, Streams, Videos


def updateStreamById(video_id, metadata):
  # update stream with metadata
  theStream = Streams(url = metadata.videoUrl, videoId = metadata.videoId)
  # theStream.progCode = metadata.progName
  theStream.progCode = metadata.progCode
  theStream.networkName = metadata.networkName
  theStream.progMetadata = json.dumps(metadata)
  theStream.dateLastChecked = datetime.datetime.utcnow
  theStream.status = "done"
  theStream.save()
  return theStream


def getStreamById(video_id):
  streams = Streams.objects(videoId = video_id)
  if len(streams) == 0:
    return None
    
  theStream = streams[0]
  return theStream


def addVideo(dstFullPath, folder, progMetadata, theStream):
  theVideo = Videos(path=dstFullPath)
  theVideo.progCode = progMetadata.progCode
  theVideo.networkName = progMetadata.networkName
  theVideo.filename = progMetadata.filename
  theVideo.folder = folder
  theVideo.title = progMetadata.title
  theVideo.duration = progMetadata.duration
  theVideo.sypnosis = progMetadata.sypnosis
  theVideo.firstAirDate = progMetadata.firstAirDate
  theVideo.stream = theStream
  theVideo.save()
  return theVideo
