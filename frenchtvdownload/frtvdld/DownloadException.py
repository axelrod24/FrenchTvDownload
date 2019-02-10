#!/usr/bin/env python
# -*- coding:Utf-8 -*-


#
# Modules
#

#from exceptions import Exception

class FrTvDownloadException(Exception):
    """
    Exception
    """
    pass


class FrTvDwnVideoNotFound(FrTvDownloadException):
    pass

class FrTvDwnPageParsingError(FrTvDownloadException):
    pass

class FrTvDwnManifestUrlNotFoundError(FrTvDownloadException):
    pass

class FrTvDwnMetaDataParsingError(FrTvDownloadException):
    pass

class FrTvDwnUserInterruption(FrTvDownloadException):
    pass