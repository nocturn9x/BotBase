from pyrogram.errors import RPCError, FloodWait
from pyrogram import Client
import time
import logging


def send_message(client: Client, sleep: bool = True, *args, **kwargs):
    """Sends a message in a way that never triggers exceptions and logs errors

       :param client: The pyrogram.Client instance to call the method for
       :type client: class: Client
       :param sleep: If True, the default, the function will call time.sleep()
       in case of a FloodWait exception and return the exception object
       after the sleep is done, otherwise the ``FloodWait`` exception is returned
       immediately
    """

    try:
        return client.send_message(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! A wait of {fw.x} seconds is required")
        if sleep:
           time.sleep(fw.x)
       return fw
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return generic_error


def send_photo(client: Client, sleep: bool = True, *args, **kwargs):
    """Sends a photo in a way that never triggers exceptions and logs errors

       :param client: The pyrogram.Client instance to call the method for
       :type client: class: Client
       :param sleep: If True, the default, the function will call time.sleep()
       in case of a FloodWait exception and return the exception object
       after the sleep is done, otherwise the ``FloodWait`` exception is returned
       immediately
    """

    try:
        return client.send_photo(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! A wait of {fw.x} seconds is required")
        if sleep:
           time.sleep(fw.x)
       return fw
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return generic_error


def send_audio(client: Client, sleep: bool = True, *args, **kwargs):
    """Sends an audio in a way that never triggers exceptions and logs errors

       :param client: The pyrogram.Client instance to call the method for
       :type client: class: Client
       :param sleep: If True, the default, the function will call time.sleep()
       in case of a FloodWait exception and return the exception object
       after the sleep is done, otherwise the ``FloodWait`` exception is returned
       immediately
    """

    try:
        return client.send_audio(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! A wait of {fw.x} seconds is required")
        if sleep:
           time.sleep(fw.x)
       return fw
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return generic_error


def send_sticker(client: Client, sleep: bool = True, *args, **kwargs):
    """Sends a sticker in a way that never triggers exceptions and logs errors

       :param client: The pyrogram.Client instance to call the method for
       :type client: class: Client
       :param sleep: If True, the default, the function will call time.sleep()
       in case of a FloodWait exception and return the exception object
       after the sleep is done, otherwise the ``FloodWait`` exception is returned
       immediately
    """
    try:
        return client.send_sticker(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! A wait of {fw.x} seconds is required")
        if sleep:
           time.sleep(fw.x)
       return fw
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return generic_error


def send_animation(client: Client, sleep: bool = True, *args, **kwargs):
    """Sends an animation in a way that never triggers exceptions and logs errors

       :param client: The pyrogram.Client instance to call the method for
       :type client: class: Client
       :param sleep: If True, the default, the function will call time.sleep()
       in case of a FloodWait exception and return the exception object
       after the sleep is done, otherwise the ``FloodWait`` exception is returned
       immediately
    """
    try:
        return client.send_animation(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! A wait of {fw.x} seconds is required")
        if sleep:
           time.sleep(fw.x)
       return fw
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return generic_error



