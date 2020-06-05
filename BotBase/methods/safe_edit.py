from pyrogram.errors import RPCError, FloodWait
import time
import logging


def edit_message_text(update, *args, **kwargs):
    """Edits a message in a way that never triggers exceptions and logs errors"""

    try:
        return update.edit_message_text(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! Sleeping {fw.x} seconds")
        time.sleep(fw.x)
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return False


def edit_message_caption(update, *args, **kwargs):
    """Edits a message caption in a way that never triggers exceptions and logs errors"""

    try:
        return update.edit_message_caption(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! Sleeping {fw.x} seconds")
        time.sleep(fw.x)
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return False


def edit_message_media(update, *args, **kwargs):
    """Edits a message media in a way that never triggers exceptions and logs errors"""

    try:
        return update.edit_message_media(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! Sleeping {fw.x} seconds")
        time.sleep(fw.x)
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return False


