#!/usr/bin/env python
# -*- coding:Utf-8 -*-


import requests
import logging

from GlobalRef import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

userAgentList = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 appservice webview/100000']



class FakeAgent:
    def __init__(self):
        self.userAgent = userAgentList[0]

    def readBin(self, url):
        headers = {'User-Agent': self.userAgent}

        response = requests.get(url, headers=headers)
        return response.content

    def readPage(self, url):
        page = self.readBin(url)
        return page.decode('utf-8')

