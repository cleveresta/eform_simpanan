class EformServiceException(Exception):
    #blabla
    def __init__(self, message, origin, errorCode, errorMessage):
        super().__init__(message)
        self.origin = origin
        self.errorCode = errorCode
        self.errorMessage = errorMessage