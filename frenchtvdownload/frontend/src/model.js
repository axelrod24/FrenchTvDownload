
const VideoMetaData = (manifest, synopsis, progTitle, filename, mediaType, duration, videoId, drm, timeStamp, progName) => (
    {manifest: manifest, 
        synopsis: synopsis, 
        progTitle: progTitle, 
        filename: filename,
        mediaType: mediaType, 
        duration: duration, 
        videoId: videoId, 
        drm: drm, 
        timeStamp: timeStamp, 
        progName: progName})

const UrlModel = (uid, url, status, timestamp, videoMetaData) => ({uid:uid, url: url, status: status, timestamp:timestamp, metadata: videoMetaData})


export { VideoMetaData, UrlModel} ;