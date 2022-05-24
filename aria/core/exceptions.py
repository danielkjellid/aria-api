class ApplicationError(Exception):
    def __init__(self, message, extra=None, status_code=400):
        super().__init__(message)

        self.message = message
        self.extra = extra or {}
        self.status_code = status_code
