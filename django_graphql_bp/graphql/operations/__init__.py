FORBIDDEN_ACCESS_ERROR = '403 Forbidden Access'
UNAUTHORIZED_ERROR = '401 Unauthorized'


def raise_forbidden_access_error():
    raise PermissionError(FORBIDDEN_ACCESS_ERROR)


def raise_unathorized_error():
    raise PermissionError(UNAUTHORIZED_ERROR)
