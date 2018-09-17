#!/usr/bin/env python
# -*- coding:Utf-8 -*-

import logging
import os
import re
import threading

from GlobalRef import LOGGER_NAME
from FakeAgent import FakeAgent
from DownloadException import FrTvDownloadException

logger = logging.getLogger(LOGGER_NAME)

kw = ["SUBTITLES", "AUDIO", "PROGRAM-ID", "BANDWIDTH" , "RESOLUTION", "CODECS"]

class HlsManifestParser(object):
    """
    Download and parse Hls manifest
    """
    def __init__(self, fakeAgent, url):
        self.fakeAgent = fakeAgent
        self.manifestUrl = url
        self.HlsManifest = self.fakeAgent.readPage(self.manifestUrl)
        self.data = {}
        self._parseManifest()

    def _parseManifest(self):
        lines = self.HlsManifest.split("\n")
        i = 0
        while(i<len(lines)):
            l = lines[i] 
            if l.startswith("#EXT-X-STREAM-INF:"):
                streamInfMeta = self._parseStreamInf(l)
                streamInfMeta["URL"] = lines[i+1]
                self.data[streamInfMeta["WIDTH"]] = streamInfMeta
                i+=2
                continue

            i+=1

    def _parseStreamInf(self, line):
        metadata = {}
        line = line[line.find(":")+1:]

        while(len(line)>0):
            # treat special case of CODECS which can't be split on ","
            if line.startswith("CODECS"):
                k, v = line.split("=", 1)
                lastindex = v.find('"', 1)
                metadata[k] = v[:lastindex+1].strip('"')
                line = v[lastindex+1:]
                continue
            
            # split on "," but get only first split
            elt = line.split(",", 1)
            k, v = elt[0].split("=")
            if k == "RESOLUTION":
                w, h = v.split("x") 
                metadata["WIDTH"] = int(w)
                metadata["HEIGHT"] = int(h)

            elif k == "BANDWIDTH":
                metadata[k] = int(v.strip('"'))

            else:
                metadata[k] = v.strip('"')

            line = elt[1]

        return metadata

    def listOfResolutions(self):
        l=[]
        for meta in self.data:
            l.append(str(self.data[meta]["WIDTH"])+"x"+str(self.data[meta]["HEIGHT"]))

        return l

    def getHighestResolutionStream(self):
        maxR = 0 
        for k in self.data.keys():
            if k > maxR:
                maxR = k
        return self.data[maxR]

    def getListOfSegment(self, url):
        manifest = self.fakeAgent.readPage(url)
        listFragments = []
        listFragments.extend(re.findall(".+?\.ts", manifest))
        return listFragments
 


class HLSStreamDownloader(object):
    """
    Download m3u8 file and segmets
    """

    def __init__(self, fakeAgent, seglist, stopDownloadEvent=threading.Event()):
        self.listOfSegments = seglist
        self.fakeAgent = fakeAgent
        self.stopDownloadEvent = stopDownloadEvent

    def download(self, toFile, progressFnct):

        maxNbrFrag = len(self.listOfSegments)
        logger.info("Nbr of fragments : %d" % (maxNbrFrag))

        #p
        # Create video file
        #
        try:
            videoFile = open(toFile, "wb")
        except:
            raise FrTvDownloadException("Can't create video file")

        logger.info("Created: %s" % toFile)

        # Download fragments and create the ts file
        logger.info("Start downloading fragments")
        try:
            i = 0
            while i < maxNbrFrag and not self.stopDownloadEvent.isSet():
                frag = self.fakeAgent.readBin(self.listOfSegments[i])
                videoFile.write(frag)

                # display progress
                i += 1
                progressFnct((i,maxNbrFrag))
                # progressFnct(min(int((i * 100) / maxNbrFrag), 100))

            if i == maxNbrFrag:
                progressFnct((maxNbrFrag,maxNbrFrag))
                logger.info("Download completed")
                videoFile.close()

        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt")
            raise FrTvDownloadException("Keyboard Interrupt")

        except Exception as inst:
            logger.critical("Critical error %s" % inst)
            # remove the file ... (cleanup)
            videoFile.close()
            if os.path.isfile(toFile):
                os.remove(toFile)

            raise FrTvDownloadException("Critical error %s" % (inst))

        finally:
            if i != maxNbrFrag:
                logger.critical("Couldn't complete video download.  Stop at fragment %d/%d" % (i, maxNbrFrag))

            return toFile



# if (__name__ == "__main__"):
#     url = 'http://replayftv-vh.akamaihd.net/i/streaming-adaptatif/2018/S37/J2/186788763-5b97f442b65e5-,standard1,standard2,standard3,standard4,standard5,.mp4.csmil/master.m3u8?caption=2018%2F37%2F186788763-1536685602.m3u8%3Afra%3AFrancais&audiotrack=0%3Afra%3AFrancais'

#     hlsDownloader = HlsDownloader(FakeAgent(), url)
#     print(hlsDownloader.listOfResolutions())
#     hrs = hlsDownloader.getHighestResolutionStream()
#     print(hrs)
#     l = hlsDownloader.getListOfSegment(hrs["URL"])
#     for s in l:
#         print(s)