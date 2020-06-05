from pyrogram.errors import RPCError, FloodWait
from pyrogram import Client
import time
import logging


def send_message(client: Client, *args, **kwargs):
    """Sends a message in a way that never triggers exceptions and logs errors"""

    try:
        return client.send_message(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! Sleeping {fw.x} seconds")
        time.sleep(fw.x)
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return False


def send_photo(client: Client, *args, **kwargs):
    """Sends a photo in a way that never triggers exceptions and logs errors"""

    try:
        return client.send_photo(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! Sleeping {fw.x} seconds")
        time.sleep(fw.x)
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return False


def send_audio(client: Client, *args, **kwargs):
    """Sends an audio in a way that never triggers exceptions and logs errors"""

    try:
        return client.send_audio(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! Sleeping {fw.x} seconds")
        time.sleep(fw.x)
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return False


def send_sticker(client: Client, *args, **kwargs):
    """Sends a sticker in a way that never triggers exceptions and logs errors"""

    try:
        return client.send_sticker(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! Sleeping {fw.x} seconds")
        time.sleep(fw.x)
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return False


def send_animation(client: Client, *args, **kwargs):
    """Sends an animation in a way that never triggers exceptions and logs errors"""

    try:
        return client.send_animation(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! Sleeping {fw.x} seconds")
        time.sleep(fw.x)
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return False



