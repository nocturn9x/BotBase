import logging
from pyrogram import Client
import sqlite3.dbapi2 as sqlite3
import os
from pyrogram.session import Session
import importlib


def create_database(path: str, query: str):
    if os.path.exists(path):
        logging.warning(f"Database file exists at {path}, running query")
    else:
        logging.warning(f"No database found, creating it at {path}")
    try:
        database = sqlite3.connect(path)
    except sqlite3.Error as connection_error:
        logging.error(f"An error has occurred while connecting to database: {connection_error}")
    else:
        try:
            with database:
                cursor = database.cursor()
                cursor.executescript(query)
                cursor.close()
        except sqlite3.Error as query_error:
            logging.info(f"An error has occurred while executing query: {query_error}")


if __name__ == "__main__":
    MODULE_NAME = "BotBase"
    conf = importlib.import_module(MODULE_NAME)
    logging.basicConfig(format=conf.LOGGING_FORMAT, datefmt=conf.DATE_FORMAT, level=conf.LOGGING_LEVEL)
    bot = Client(api_id=conf.API_ID, api_hash=conf.API_HASH, bot_token=conf.BOT_TOKEN, plugins=conf.PLUGINS_ROOT,
                 session_name=conf.SESSION_NAME, workers=conf.WORKERS_NUM)
    Session.notice_displayed = True
    try:
        logging.warning("Running create_database()")
        create_database(conf.DB_RELPATH, conf.DB_CREATE)
        logging.warning("Database interaction complete")
        logging.warning("Starting bot")
        bot.start()
        logging.warning("Bot started")
    except KeyboardInterrupt:
        logging.warning("Stopping bot")
        bot.stop()
