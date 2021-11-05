import inspect
from typing import Any, Callable


def get_valid_call(func: Callable, args_dict) -> dict:
    """
    Returns a dictionary of valid arguemnts for the supplied function. if kwargs are accepted,
    the original dictionary will be returned.
    """

    def get_valid_args(func: Callable) -> tuple:
        """
        Returns a tuple of valid arguemnts for the supplied function.
        """
        return inspect.getfullargspec(func).args

    def accepts_kwargs(func: Callable) -> bool:
        """
        Returns True if the function accepts keyword arguments.
        """
        return inspect.getfullargspec(func).varkw is not None

    if accepts_kwargs(func):
        return args_dict

    valid_args = get_valid_args(func)

    return {k: v for k, v in args_dict.items() if k in valid_args}


def safe_call(func, dict_args, **kwargs) -> Any:
    """
    Safely calls the supplied function with the supplied dictionary of arguments.
    by removing any invalid arguments.
    """

    if kwargs:
        dict_args.update(kwargs)

    try:
        return func(**get_valid_call(func, dict_args))
    except TypeError:
        return func(**dict_args)
