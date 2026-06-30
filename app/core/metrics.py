from contextvars import ContextVar

_query_count: ContextVar[int] = ContextVar("query_count", default=0)


def reset_query_count() -> None:
    _query_count.set(0)


def increment_query_count() -> None:
    _query_count.set(_query_count.get() + 1)


def get_query_count() -> int:
    return _query_count.get()
