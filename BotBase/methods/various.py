from pyrogram.errors import RPCError, FloodWait
import time
from pyrogram import CallbackQuery
import logging


def answer(query: CallbackQuery, sleep: bool = True, *args, **kwargs):
    """Answers a query in a way that never triggers exceptions and logs errors

       :param update: The pyrogram.CallbackQuery object to call the method for
       :type update: class: CallbackQuery
       :param sleep: If True, the default, the function will call time.sleep()
       in case of a FloodWait exception and return the exception object
       after the sleep is done, otherwise the ``FloodWait`` exception is returned
       immediately
       :returns: Whatever the called pyrogram method returns, or an exception if
       the method call caused an error
    """

    try:
        return query.answer(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! A wait of {fw.x} seconds is required")
        if sleep:
            time.sleep(fw.x)
        return fw
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return generic_error


def delete_messages(client, sleep: bool = True, *args, **kwargs):
    """Deletes messages in a way that never triggers exceptions and logs errors"""

    try:
        return client.delete_messages(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! A wait of {fw.x} seconds is required")
        if sleep:
            time.sleep(fw.x)
        return fw
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return generic_error
