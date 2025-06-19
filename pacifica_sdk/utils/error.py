class Error(Exception):
    pass


class ApiError(Error):
    def __init__(
        self,
        status_code: int,
        code: int | None,
        error_message: str | None,
        data: any,
        raw_body: str,
    ):
        self.status_code = status_code
        self.code = code
        self.error_message = error_message
        self.data = data
        self.raw_body = raw_body
        super().__init__(f"[{status_code}] code={code} message={error_message!r} data={data!r}")


class ServerError(Error):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"ServerError({status_code}): {message!r}")
