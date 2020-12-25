class SnackResponse:
    @staticmethod
    def _create_response(message: str, type: str) -> dict:
        return {"snackbar": {"text": message, "type": type}}

    @staticmethod
    def primary(message: str) -> dict:
        return SnackResponse._create_response(message, "primary")

    @staticmethod
    def accent(message: str) -> dict:
        return SnackResponse._create_response(message, "accent")

    @staticmethod
    def secondary(message: str) -> dict:
        return SnackResponse._create_response(message, "secondary")

    @staticmethod
    def success(message: str) -> dict:
        return SnackResponse._create_response(message, "success")

    @staticmethod
    def info(message: str) -> dict:
        return SnackResponse._create_response(message, "info")

    @staticmethod
    def warning(message: str) -> dict:
        return SnackResponse._create_response(message, "warning")

    @staticmethod
    def error(message: str) -> dict:
        return SnackResponse._create_response(message, "error")
