#!/usr/bin/env python
# -*- coding:Utf-8 -*-


import requests
import logging

from GlobalRef import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

userAgentList = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 appservice webview/100000',
    "Mozilla/5.0 (iPad; CPU OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13F69 Safari/601.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15"]


class FakeAgent:
    def __init__(self):
        self.userAgent = userAgentList[2]

    def readBin(self, url):
        headers = {'User-Agent': self.userAgent}

        response = requests.get(url, headers=headers)
        return response.content

    def readPage(self, url):
        logger.info("read: %s" % url)
        page = self.readBin(url)
        return page.decode('utf-8')

