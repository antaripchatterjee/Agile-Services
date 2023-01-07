class WrongStatusCodeByServiceError(Exception):
    pass

class WrongResponseModelByServiceError(Exception):
    pass


class HTTPRequestError(Exception):
    def __init__(self, *, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super(HTTPRequestError, self).__init__(f'HTTP error {status_code} : {message}')

