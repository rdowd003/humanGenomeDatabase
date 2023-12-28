import logging
import os

import sys, os, functools
from inspect import getframeinfo, stack

from configs import auto_config as cfg


class CustomFormatter(logging.Formatter):
    """ Custom Formatter does these 2 things:
    1. Overrides 'funcName' with the value of 'func_name_override', if it exists.
    2. Overrides 'filename' with the value of 'file_name_override', if it exists.
    """

    def format(self, record):
        if hasattr(record, 'func_name_override'):
            record.funcName = record.func_name_override
        if hasattr(record, 'file_name_override'):
            record.filename = record.file_name_override
        return super(CustomFormatter, self).format(record)

# Logger Initialization
def get_logger(log_file_name, log_sub_dir=""):
    """ Creates a Log File and returns Logger object """

    windows_log_dir = 'c:\\logs_dir\\'
    linux_log_dir = 'logs_dir/'

    # Build Log file directory, based on the OS and supplied input
    log_dir = windows_log_dir if os.name == 'nt' else linux_log_dir
    log_dir = os.path.join(log_dir, log_sub_dir)

    # Create Log file directory if not exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Build Log File Full Path
    logPath = log_file_name if os.path.exists(log_file_name) else os.path.join(log_dir, (str(log_file_name) + '.log'))

    # Create logger object and set the format for logging and other attributes
    logger = logging.Logger(log_file_name)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(logPath, 'a+')
    """ Set the formatter of 'CustomFormatter' type as we need to log base function name and base file name """
    handler.setFormatter(CustomFormatter('%(asctime)s - %(levelname)-10s - %(filename)s - %(funcName)s - %(message)s'))
    logger.addHandler(handler)

    # Return logger object
    return logger


# Log Decorator Function
def log(_func=None):
    def log_decorator_info(func):
        @functools.wraps(func)
        def log_decorator_wrapper(self, *args, **kwargs):
            # Build logger object
            logger_obj = get_logger(log_file_name=self.log_file_name, log_sub_dir=self.log_file_dir)

            """ Create a list of the positional arguments passed to function.
            - Using repr() for string representation for each argument. repr() is similar to str() only difference being
             it prints with a pair of quotes and if we calculate a value we get more precise value than str(). """
            args_passed_in_function = [repr(a) for a in args]
            """ Create a list of the keyword arguments. The f-string formats each argument as key=value, where the !r 
                specifier means that repr() is used to represent the value. """
            kwargs_passed_in_function = [f"{k}={v!r}" for k, v in kwargs.items()]

            """ The lists of positional and keyword arguments is joined together to form final string """
            formatted_arguments = ", ".join(args_passed_in_function + kwargs_passed_in_function)

            """ Generate file name and function name for calling function. __func.name__ will give the name of the 
                caller function ie. wrapper_log_info and caller file name ie log-decorator.py
            - In order to get actual function and file name we will use 'extra' parameter.
            - To get the file name we are using in-built module inspect.getframeinfo which returns calling file name """
            py_file_caller = getframeinfo(stack()[1][0])
            extra_args = { 'func_name_override': func.__name__,
                           'file_name_override': os.path.basename(py_file_caller.filename) }

            """ Before to the function execution, log function details."""
            logger_obj.info(f"Arguments: {formatted_arguments} - Begin function")
            try:
                """ log return value from the function """
                value = func(self, *args, **kwargs)
                logger_obj.info(f"Returned: - End function {value!r}")
            except:
                """log exception if occurs in function"""
                logger_obj.error(f"Exception: {str(sys.exc_info()[1])}")
                raise
            # Return function value
            return value
        # Return the pointer to the function
        return log_decorator_wrapper
    # Decorator was called with arguments, so return a decorator function that can read and return a function
    if _func is None:
        return log_decorator_info
    # Decorator was called without arguments, so apply the decorator to the function immediately
    else:
        return log_decorator_info(_func)