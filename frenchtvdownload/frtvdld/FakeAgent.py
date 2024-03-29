import requests
import logging

from frtvdld.GlobalRef import LOGGER_NAME
from frtvdld.DownloadException import FrTvDwnConnectionError

logger = logging.getLogger(LOGGER_NAME)

userAgentList = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 appservice webview/100000',
    "Mozilla/5.0 (iPad; CPU OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13F69 Safari/601.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15"]

CURRENT_USER_AGENT = userAgentList[-1]


class FakeAgent:
  def __init__(self):
    self.userAgent = CURRENT_USER_AGENT

  def readBin(self, url):
    headers = {'User-Agent': self.userAgent}
    try:
      response = requests.get(url, headers=headers)
      if response.status_code != 200:
        raise FrTvDwnConnectionError("Status code:%d" % response.status_code)

      # response.encoding = response.apparent_encoding

    except ConnectionError as e:
      raise FrTvDwnConnectionError(e.__repr__())

    # print(response.content)
    return response.content

  def readPage(self, url):
    logger.info("read: %s" % url)
    page = self.readBin(url)
    # return page
    return page.decode('utf-8')
