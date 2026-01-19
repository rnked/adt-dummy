"""Custom error types for CLI-friendly failures."""


class AppError(Exception):
    def __init__(self, message, exit_code=1):
        super().__init__(message)
        self.exit_code = exit_code
