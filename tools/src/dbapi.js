const mongoose = require('mongoose') ;
const localcfg = require('./localcfg')


mongoose.connect(localcfg.MONGO_URL)
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('Could not connect o MongoDB ...', err))


const streamSchema= new mongoose.Schema({
  url: String,
  progCode: String,
  networkName: String,
  dateAdded: Date,
  status: String,
  videoId: String,
  progMetadata: String,
  dateLastChecked: Date,
//   lastErrors = EmbeddedDocumentListField(Errors)
}) ;

const videoSchema = new mongoose.Schema({
  path: String,
  dateAdded: Date,
  progCode: String,
  networkName: String,
  repo: String,
  filename: String,
  folder: String,
  codecs: String,
  title: String,
  duration: Number,
  firstAirDate: Date,
  synopsis: String,
  // stream = ReferenceField(Streams)
}) ;

const Video = new mongoose.model('Video', videoSchema) ;

async function getAllVideo() {
  const allVideos = await Video.find({repo:"VM1"}).sort({dateAdded: 1}); 
  return allVideos
}

exports.getAllVideo = getAllVideo ;
