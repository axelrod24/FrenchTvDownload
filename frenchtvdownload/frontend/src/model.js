
const VideoMetaData = (manifest, synopsis, progTitle, filename, videoFullpath, mediaType, duration, videoId, drm, timeStamp, progName) => (
    {manifest: manifest, 
        synopsis: synopsis, 
        progTitle: progTitle, 
        filename: filename,
        videoFullPath: videoFullpath,
        mediaType: mediaType, 
        duration: duration, 
        videoId: videoId, 
        drm: drm, 
        timeStamp: timeStamp, 
        progName: progName})

const UrlModel = (uid, url, status, timestamp, videoMetaData) => ({uid:uid, url: url, status: status, timestamp:timestamp, metadata: videoMetaData})


const MapVideoModelToAppModel = (data) => {

    var vmd = (!data.mdata || data.mdata.length === 0) ? VideoMetaData() : (() => {
    
        var d = JSON.parse(data.mdata)
        return VideoMetaData(d.manifestUrl, d.synopsis, d.progTitle, d.filename, d.videoFullPath, d.mediaType, d.duration, d.videoId, d.drm, d.timeStamp, d.progName) 
    })()

    var um = UrlModel(data.video_id, data.url, data.status, new Date(data.timestamp).getTime(), vmd)
    return um
}

export { VideoMetaData, UrlModel, MapVideoModelToAppModel} ;