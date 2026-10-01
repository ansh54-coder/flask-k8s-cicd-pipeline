class APIError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(APIError):
    def __init__(self, message):
        super().__init__(message, 400)


class NotFoundError(APIError):
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404)


class UnauthorizedError(APIError):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, 401)


class ForbiddenError(APIError):
    def __init__(self, message="Forbidden"):
        super().__init__(message, 403)


class ConflictError(APIError):
    def __init__(self, message):
        super().__init__(message, 409)
