import logging
from pyrogram import Client
from pyrogram.session import Session
from BotBase.config import bot, LOGGING_LEVEL, LOGGING_FORMAT, DATE_FORMAT, DB_PATH, DB_CREATE
from BotBase.database.query import create_database


if __name__ == "__main__":
    logging.basicConfig(format=LOGGING_FORMAT, datefmt=DATE_FORMAT, level=LOGGING_LEVEL)
    Session.notice_displayed = True
    try:
        logging.warning("Running create_database()")
        create_database(DB_PATH, DB_CREATE)
        logging.warning("Database interaction complete")
        logging.warning("Starting bot")
        bot.start()
        logging.warning("Bot started")
    except Exception as e:
        logging.warning(f"Stopping bot due to a {type(e).__name__}: {e}")
        bot.stop()
