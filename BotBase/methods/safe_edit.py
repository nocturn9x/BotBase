from pyrogram.errors import RPCError, FloodWait
import time
import logging
from pyrogram import Client, CallbackQuery
from typing import Union


def edit_message_text(update: Union[CallbackQuery, Client], sleep: bool = True, *args, **kwargs):
    """Edits a message in a way that never triggers exceptions and logs errors

       :param update: The pyrogram.Client instance or pyrogram.CallbackQuery
       object to call the method for
       :type update: Union[Client, CallbackQuery]
       :param sleep: If True, the default, the function will call time.sleep()
       in case of a FloodWait exception and return the exception object
       after the sleep is done, otherwise the ``FloodWait`` exception is returned
       immediately
       :returns: Whatever the called pyrogram method returns, or an exception if
       the method call caused an error
    """

    try:
        return update.edit_message_text(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! A wait of {fw.x} seconds is required")
        if sleep:
            time.sleep(fw.x)
        return fw
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return generic_error


def edit_message_caption(update: Union[CallbackQuery, Client], sleep: bool = True, *args, **kwargs):
    """Edits a message caption in a way that never triggers exceptions and logs errors

       :param update: The pyrogram.Client instance or pyrogram.CallbackQuery
       object to call the method for
       :type update: Union[Client, CallbackQuery]
       :param sleep: If True, the default, the function will call time.sleep()
       in case of a FloodWait exception and return the exception object
       after the sleep is done, otherwise the ``FloodWait`` exception is returned
       immediately
       :returns: Whatever the called pyrogram method returns, or an exception if
       the method call caused an error
    """

    try:
        return update.edit_message_caption(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! A wait of {fw.x} seconds is required")
        if sleep:
            time.sleep(fw.x)
        return fw
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return generic_error


def edit_message_media(update: Union[CallbackQuery, Client], sleep: bool = True, *args, **kwargs):
    """Edits a message media in a way that never triggers exceptions and logs errors

       :param update: The pyrogram.Client instance or pyrogram.CallbackQuery
       object to call the method for
       :type update: Union[Client, CallbackQuery]
       :param sleep: If True, the default, the function will call time.sleep()
       in case of a FloodWait exception and return the exception object
       after the sleep is done, otherwise the ``FloodWait`` exception is returned
       immediately
       :returns: Whatever the called pyrogram method returns, or an exception if
       the method call caused an error
     """

    try:
        return update.edit_message_media(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! A wait of {fw.x} seconds is required")
        if sleep:
            time.sleep(fw.x)
        return fw
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return generic_error

