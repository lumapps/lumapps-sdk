# -*- coding: utf-8 -*-
"""
Common exceptions used server-side
"""
import logging
import httplib


class CustomException(Exception):
    """
    Represent a custom exception
    """

    http_status = httplib.INTERNAL_SERVER_ERROR
    info = None

    def __init__(self, message="", info=None):
        """
        Constructor, take a message in parameter
        @param message: the exception message
        @param info: an additional info to log
        """
        super(Exception, self).__init__(
            message or self.message, httplib.responses[self.http_status]
        )
        self.info = info
        logging.warning(
            "%s.__init__ - %s %s",
            self.__class__.__name__,
            self.message,
            ("({})".format(self.info)) if self.info else "",
        )


class NotFoundException(CustomException):
    """
    Represent a not found error
    """

    http_status = httplib.NOT_FOUND


class NotAuthorizedException(CustomException):
    """
    Represent a not authorized error
    """

    http_status = httplib.FORBIDDEN


class MissingFieldException(CustomException):
    """
    Represent a missing field error
    """

    http_status = httplib.BAD_REQUEST


class BadRequestException(CustomException):
    """
    Represent a bad request exception
    """

    http_status = httplib.BAD_REQUEST


class AuthorizationRequiredException(CustomException):
    """
    Represent a request that need authorization
    """

    http_status = httplib.UNAUTHORIZED


class DuplicatedException(CustomException):
    """
    Represent a request that need authorization
    """

    http_status = httplib.CONFLICT


class InternalErrorException(CustomException):
    http_status = httplib.INTERNAL_SERVER_ERROR
