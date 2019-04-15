#!/usr/bin/env python
# -*- coding:Utf-8 -*-


#
# Modules
#

#from exceptions import Exception

class FrTvDownloadException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.custom_msg = "Unknown download exception"

    def __repr__(self):
        return ("%s - %s" % (self.custom_msg, super().__repr__()))

    def __str__(self):
        return self.__repr__()

class FrTvDwnUserInterruption(FrTvDownloadException):
    def __init__(self, message):
        super().__init__(message)
        self.custom_msg = "Download interupted by user."

class FrTvDwnConnectionError(FrTvDownloadException):
    def __init__(self, message):
        super().__init__(message)
        self.custom_msg = "Network connection error."

class FrTvDwnVideoNotFound(FrTvDownloadException):
   def __init__(self, message):
        super().__init__(message)
        self.custom_msg = "Can't find video."


class FrTvDwnPageParsingError(FrTvDownloadException):
   def __init__(self, message):
        super().__init__(message)
        self.custom_msg = "Can't find video ID."


class FrTvDwnMetaDataParsingError(FrTvDownloadException):
    def __init__(self, message):
        super().__init__(message)
        self.custom_msg = "Can't parse video metadata."


class FrTvDwnManifestError(FrTvDownloadException):
    def __init__(self, message):
        super().__init__(message)
        self.custom_msg = "Can't download manifest."


class FrTvDwnSegmentError(FrTvDownloadException):
    def __init__(self, message):
        super().__init__(message)
        self.custom_msg = "Can't download segments."

