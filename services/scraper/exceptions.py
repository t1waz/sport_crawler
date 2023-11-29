class AppException(Exception):
    pass


class SpiderTimeoutException(AppException):
    pass


class SpiderNetworkException(AppException):
    pass


class SpiderNotFinished(AppException):
    pass


class SpiderParseDataException(AppException):
    pass
