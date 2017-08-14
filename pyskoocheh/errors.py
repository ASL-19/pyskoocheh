""" Holds local library error types """

class PyskoochehException(Exception):
    """ Base class for exceptions in Pyskoocheh """
    def __init__(self, value):
        """ Set value of error message """
        super(PyskoochehException, self).__init__()
        self.value = value
    def __str__(self):
        """ Output representation of error """
        return repr(self.value)

class AWSError(PyskoochehException):
    """ AWS API Error Wrapper """

class FeedbackError(PyskoochehException):
    """ Feedback Error Wrapper """

class TelegramError(PyskoochehException):
    """ Telegram Error Wrapper """

class ValidationError(PyskoochehException):
    """ Validation Error Wrapper """

class HTTPError(PyskoochehException):
    """ HTTP Error on Requests """
