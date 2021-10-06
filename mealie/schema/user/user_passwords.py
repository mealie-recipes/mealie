from fastapi_camelcase import CamelModel


class ForgotPassword(CamelModel):
    email: str


class ValidateResetToken(CamelModel):
    token: str


class ResetPassword(ValidateResetToken):
    email: str
    password: str
    passwordConfirm: str
