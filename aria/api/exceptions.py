class PageOutOfBoundsError(Exception):
    def __init__(
        self, message="Page out of bounds - we are not able to find that page"
    ):
        super().__init__(message)
        self.message = message
