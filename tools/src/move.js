//include the fs, path modules
const fs = require('fs');
const path = require('path');

const localcfg = require('./localcfg')
const dbapi = require('./dbapi')


//moves the $file to $dir2
function moveFile(file, dir2) {

  //gets file name and adds it to dir2
  var f = path.basename(file);
  var dest = path.resolve(dir2, f);

  fs.rename(file, dest, (err)=>{
    if(err) throw err;
    else console.log('Successfully moved');
  });
};

function processEachEntry(video) {
  const folder = video.folder
  const filename = video.filename+".mp4"
  const srcPath = path.join(localcfg.SRC_BASE_PATH,folder,filename)
  const dstPath = path.join(localcfg.DST_BASE_PATH,folder,filename)

  console.log("moving:"+srcPath+" to "+dstPath)
}

dbapi.getAllVideo().then(videos => videos.forEach(processEachEntry))





  
  