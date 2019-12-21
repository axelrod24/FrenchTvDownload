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

  fs.renameSync(file, dest, (err)=>{
    if(err) throw err;
    else console.log('Successfully moved');
  });
};

function processEachEntry(video) {
  const folder = video.folder
  const filename = video.filename+".mp4"
  const metafilename = video.filename+".meta"
  console.log("Processing:"+folder+"/"+filename)

  const srcPath = path.join(localcfg.SRC_BASE_PATH,folder,filename)
  const srcPathMeta = path.join(localcfg.SRC_BASE_PATH,folder,metafilename)
  const dstPath = path.join(localcfg.DST_BASE_PATH,folder)

  // create dst folder if doesn't exists
  if (!fs.existsSync(dstPath)) {
    console.log("Creating:"+dstPath)
    fs.mkdirSync(dstPath)
  }

  // move mp4 file
  if (fs.existsSync(srcPath)) {
    console.log("moving:"+srcPath)
    fs.renameSync(srcPath, path.join(dstPath, filename))
  }
  
  // move meta file
  if (fs.existsSync(srcPathMeta)) {
    console.log("moving:"+srcPathMeta)
    fs.renameSync(srcPathMeta, path.join(dstPath, metafilename))
  }
  
  console.log("moved:"+srcPath+" to "+dstPath)
}

dbapi.getAllVideo().then(videos => videos.forEach(processEachEntry))





  
  