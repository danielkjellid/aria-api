class ApplicationError(Exception):
    def __init__(
        self, message: str, extra: dict[str, str] | None = None, status_code: int = 400
    ) -> None:
        super().__init__(message)

        self.message = message
        self.extra = extra or {}
        self.status_code = status_code
