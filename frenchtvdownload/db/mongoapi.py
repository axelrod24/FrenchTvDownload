import datetime, json, os, logging
from db.mongomodels import Errors, Channels, Streams, Videos


def updateStreamById(video_id, metadata):
  # update stream with metadata
  theStream = Streams(url = metadata.videoUrl, videoId = metadata.videoId)
  # theStream.progCode = metadata.progName
  theStream.manifestUrl = metadata.manifestUrl
  theStream.progMetadata = json.dumps(metadata)
  theStream.dateLastChecked = datetime.datetime.utcnow
  theStream.status = "done"
  theStream.save()
  return


def getStreamById(video_id):
  streams = Streams.objects(videoId = video_id)
  if len(streams) == 0:
    return None
    
  theStream = streams[0]
  return theStream
