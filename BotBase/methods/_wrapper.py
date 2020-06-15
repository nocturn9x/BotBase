from pyrogram import Client, CallbackQuery, InlineQuery
from pyrogram.errors import RPCError
import logging
from typing import Union


class MethodWrapper(object):
    """A class that that implements a wrapper around ``pyrogram.Client`` methods.
       To access a pyrogram method just call ``MethodWrapper.method_name``.
       All method calls are performed in a try/except block and either return
       the exception object if an error occurs, or the result of the called
       method otherwise. All errors are automatically logged to stderr.

       :param instance: The ``pyrogram.Client`` or ``pyrogram.CallbackQuery`` or ``pyrogram.InlineQuery`` instance (not class!)
       :type instance: Union[Client, CallbackQuery, InlineQuery]
    """

    def __init__(self, instance: Union[Client, CallbackQuery, InlineQuery]):
        """Object constructor"""

        self.instance = instance

    def __getattr__(self, attribute: str):
        if attribute in self.__dict__:
            return self.__dict__[attribute]
        else:
            def wrapper(*args, **kwargs):
                if hasattr(self.instance, attribute):
                    try:
                        return getattr(self.instance, attribute)(*args, **kwargs)
                    except RPCError as err:
                        logging.error(f"An exception occurred -> {type(err).__name__}: {err}")
                        return err
                else:
                    raise AttributeError(self.instance, attribute)
            return wrapper

