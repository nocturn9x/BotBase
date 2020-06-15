from pyrogram import Client, Filters, InlineKeyboardButton, InlineKeyboardMarkup
from .antiflood import BANNED_USERS
from ..config import GREET, BUTTONS, CREDITS, CACHE, bot, VERSION, RELEASE_DATE, user_banned, BACK_BUTTON
from ..database.query import get_users, set_user
import logging
import itertools
from ..methods import MethodWrapper

wrapper = MethodWrapper(bot)


@Client.on_message(Filters.command("start") & ~BANNED_USERS & Filters.private & ~user_banned())
def start_handler(client, message):
    """Simply handles the /start command sending a pre-defined greeting
    and saving new users to the database"""

    if message.from_user.first_name:
        name = message.from_user.first_name
    elif message.from_user.username:
        name = message.from_user.username
    else:
        name = "Anonymous"
    if message.from_user.id not in itertools.chain(*get_users()):
        logging.warning(f"New user detected ({message.from_user.id}), adding to database")
        set_user(message.from_user.id, message.from_user.username.lower() if message.from_user.username else None)
    if GREET:
        wrapper.send_message(message.from_user.id,
                             GREET.format(mention=f"[{name}](tg://user?id={message.from_user.id})",
                                          id=message.from_user.id,
                                          username=message.from_user.username
                                          ),
                             reply_markup=BUTTONS
                             )


@Client.on_callback_query(Filters.callback_data("info") & ~BANNED_USERS)
def bot_info(_, query):
    cb_wrapper = MethodWrapper(query)
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton(BACK_BUTTON, "back_start")]])
    cb_wrapper.edit_message_text(CREDITS.format(VERSION=VERSION, RELEASE_DATE=RELEASE_DATE), reply_markup=buttons)


@Client.on_callback_query(Filters.callback_data("back_start") & ~BANNED_USERS)
def back_start(_, query):
    cb_wrapper = MethodWrapper(query)
    if query.from_user.first_name:
        name = query.from_user.first_name
    elif query.from_user.username:
        name = query.from_user.username
    else:
        name = "Anonymous"
    if CACHE[query.from_user.id][0] == "AWAITING_ADMIN":
        data = CACHE[query.from_user.id][-1]
        if isinstance(data, list):
            for chatid, message_ids in data[:-2]:
                wrapper.delete_messages(chatid, message_ids)
    cb_wrapper.edit_message_text(GREET.format(mention=f"[{name}](tg://user?id={query.from_user.id})", id=query.from_user.id,
                                              username=query.from_user.username),
                                 reply_markup=BUTTONS)
