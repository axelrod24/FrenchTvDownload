
const VideoMetaData = (mdata) => (
    {manifest: mdata.manifestUrl, synopsis: mdata.synopsis, progTitle: mdata.progTitle, filename: mdata.filename,
        videoFullPath: mdata.videoFullPath, mediaType: mdata.mediaType, duration: mdata.duration, videoId: mdata.videoId, 
        drm: mdata.drm, timeStamp: mdata.timeStamp, progName: mdata.progName, errorMsg: mdata.errorMsg})

const UrlModel = (uid, url, status, timestamp, videoMetaData) => ({uid:uid, url: url, status: status, timestamp:timestamp, metadata: videoMetaData})


const MapVideoModelToAppModel = (data) => {

    var vmd = (!data.mdata || data.mdata.length === 0) ? VideoMetaData() : (() => {
    
                var d = JSON.parse(data.mdata)
                return VideoMetaData(d) 
            })()

    var um = UrlModel(data.video_id, data.url, data.status, new Date(data.timestamp).getTime(), vmd)
    return um
}

export { VideoMetaData, UrlModel, MapVideoModelToAppModel} ;