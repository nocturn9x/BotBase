from pyrogram.errors import RPCError, FloodWait
import time
import logging


def answer(query, *args, **kwargs):
    """Answers a query in a way that never triggers exceptions and logs errors"""

    try:
        return query.answer(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! Sleeping {fw.x} seconds")
        time.sleep(fw.x)
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return False


def delete_messages(client, *args, **kwargs):
    """Deletes messages in a way that never triggers exceptions and logs errors"""

    try:
        return client.delete_messages(*args, **kwargs)
    except FloodWait as fw:
        logging.warning(f"FloodWait! Sleeping {fw.x} seconds")
        time.sleep(fw.x)
    except RPCError as generic_error:
        logging.error(f"An exception occurred: {generic_error}")
        return False
