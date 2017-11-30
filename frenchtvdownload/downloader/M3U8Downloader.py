#!/usr/bin/env python
# -*- coding:Utf-8 -*-

import logging
import os
import re

from GlobalRef import LOGGER_NAME
from DownloadException import FrTvDownloadException

logger = logging.getLogger(LOGGER_NAME)


class M3U8Downloader(object):
    """
    Download m3u8 file and segmets
    """

    def __init__(self, m3u8URL, outputFilename, fakeAgent, stopDownloadEvent):
        self.m3u8URL = m3u8URL
        self.videoFileName = outputFilename
        self.fakeAgent = fakeAgent
        self.stopDownloadEvent = stopDownloadEvent

    def download(self, progressFnct):

        # Get fragments index: master.m3u8
        logger.info("Get index master.m3u8")
        m3u8page = self.fakeAgent.readPage(self.m3u8URL)

        # get URL of all fragments
        listFragments = re.findall(".+?\.ts", m3u8page)
        if not listFragments:
            listFragments = []
            listeM3U8 = re.findall(".+?index_2_av\.m3u8", m3u8page)
            for m3u8 in listeM3U8:
                m3u8data = self.fakeAgent.readPage(m3u8)
                listFragments.extend(re.findall(".+?\.ts", m3u8data))

        maxNbrFrag = long(len(listFragments))
        logger.info("Nbr of fragments : %d" % (maxNbrFrag))

        #
        # Create video file
        #
        try:
            videoFile = open(self.videoFileName, "wb")
        except:
            raise FrTvDownloadException("Can't create video file")

        logger.info("Created: %s" % self.videoFileName)

        # Download fragments and create the ts file
        logger.info("Start downloading fragments")
        try:
            i = 0
            while i < maxNbrFrag and not self.stopDownloadEvent.isSet():
                frag = self.fakeAgent.readPage("%s" % (listFragments[i]))
                videoFile.write(frag)

                # display progress
                progressFnct(min(int((i * 100) / maxNbrFrag), 100))
                i += 1

            if i == maxNbrFrag:
                progressFnct(100)
                logger.info("Download completed")
                videoFile.close()

        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt")
            raise FrTvDownloadException("Keyboard Interrupt")

        except Exception as inst:
            logger.critical("Critical error %s" % inst)
            # remove the file ... (cleanup)
            videoFile.close()
            if os.path.isfile(self.videoFileName):
                os.remove(self.videoFileName)

            raise FrTvDownloadException("Critical error %s" % (inst))

        finally:
            if i != maxNbrFrag:
                logger.critical("Couldn't complete video download.  Stop at fragment %d/%d" % (i, maxNbrFrag))

            return self.videoFileName

