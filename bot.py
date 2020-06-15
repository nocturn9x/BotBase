import logging
from pyrogram import CallbackQueryHandler
from pyrogram.session import Session
import importlib


if __name__ == "__main__":
    MODULE_NAME = "BotBase"  # Change this to match the FOLDER name that contains the config.py file
    conf = importlib.import_module(f"{MODULE_NAME}.config")
    bot = conf.bot
    antiflood = importlib.import_module(f"{MODULE_NAME}.modules.antiflood")
    dbmodule = importlib.import_module(f"{MODULE_NAME}.database.query")
    logging.basicConfig(format=conf.LOGGING_FORMAT, datefmt=conf.DATE_FORMAT, level=conf.LOGGING_LEVEL)
    bot.add_handler(CallbackQueryHandler(antiflood.anti_flood, ~antiflood.BYPASS_USERS), group=-1)
    Session.notice_displayed = True
    try:
        logging.warning("Running create_database()")
        dbmodule.create_database(conf.DB_PATH, conf.DB_CREATE)
        logging.warning("Database interaction complete")
        logging.warning("Starting bot")
        bot.start()
        logging.warning("Bot started")
    except Exception as e:
        logging.warning(f"Stopping bot due to a {type(e).__name__}: {e}")
        bot.stop()
