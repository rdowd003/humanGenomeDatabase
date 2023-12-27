import functools
import logging

logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger()

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.debug(f"function {func.__name__} called with args {signature}")
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
            raise e
    return wrapper

@log
def foo():
    raise Exception("Something went wrong")