def exception_message_safe(exc):
    try:
        return str(exc)
    except Exception:
        return repr(exc)


class TomeException(Exception):
    """
    Generic tome exception.
    """


class TomeConnectionError(TomeException):
    pass


# Network exceptions #
class InternalErrorException(TomeException):
    """
    Generic 500 error
    """

    pass


class RequestErrorException(TomeException):
    """
    Generic 400 error
    """

    pass


class AuthenticationException(TomeException):  # 401
    """
    401 error
    """

    pass


class ForbiddenException(TomeException):  # 403
    """
    403 error
    """

    pass


class NotFoundException(TomeException):  # 404
    """
    404 error
    """
