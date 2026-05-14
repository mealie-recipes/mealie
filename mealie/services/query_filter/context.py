from contextvars import ContextVar

allow_filter_restricted: ContextVar[bool] = ContextVar("allow_filter_restricted", default=True)
