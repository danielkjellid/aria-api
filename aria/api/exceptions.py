class PageOutOfBoundsError(Exception):
    def __init__(
        self, message: str = "Page out of bounds - we are not able to find that page"
    ) -> None:
        super().__init__(message)
        self.message = message
