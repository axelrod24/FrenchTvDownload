var path = require('path');

const VideoMetaData = (mdata) => (
    {manifest: mdata.manifestUrl, synopsis: mdata.synopsis, progTitle: mdata.progTitle, filename: mdata.filename,
        videoFullPath: mdata.videoFullPath, mediaType: mdata.mediaType, duration: mdata.duration, videoId: mdata.videoId, 
        drm: mdata.drm, timeStamp: mdata.timeStamp, progName: mdata.progName, errorMsg: mdata.errorMsg})

const UrlModel = (uid, url, status, timestamp, pathToVideo, videoMetaData) => ({uid: uid, url: url, status: status, timestamp:timestamp, 
                                                                                    pathToVideo: pathToVideo, metadata: videoMetaData})


const MapVideoModelToAppModel = (data) => {

    var vmd = (!data.mdata || data.mdata.length === 0) ? VideoMetaData() : (() => {
    
                var d = JSON.parse(data.mdata)
                return VideoMetaData(d) 
            })()

    var pathToVideo
    (data.folder_name && data.video_file_name) ? pathToVideo = path.join(data.folder_name, data.video_file_name) : pathToVideo=""
    var um = UrlModel(data.video_id, data.url, data.status, new Date(data.timestamp).getTime(), pathToVideo, vmd)
    return um
}

export { VideoMetaData, UrlModel, MapVideoModelToAppModel} ;