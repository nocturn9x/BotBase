from pyrogram import Client, Filters, InlineKeyboardButton, InlineKeyboardMarkup
from .antiflood import BANNED_USERS
from ..config import GREET, BUTTONS, CREDITS, CACHE, YOU_ARE_BANNED
from ..database.query import get_users, set_user, get_user
import logging
import itertools
from ..methods.safe_send import send_message
from ..methods.safe_edit import edit_message_text
from ..methods.various import delete_messages


def check_user_banned(tg_id: int):
    res = get_user(tg_id)
    if isinstance(res, Exception):
        return False
    else:
        if not res:
            return False
        if res[-1]:
            return True
        else:
            return False


@Client.on_message(Filters.command("start") & ~BANNED_USERS & Filters.private)
def start_handler(client, message):
    """Simply handles the /start command sending a pre-defined greeting
    and saving new users to the database"""

    if message.from_user.first_name:
        name = message.from_user.first_name
    elif message.from_user.username:
        name = message.from_user.username
    else:
        name = "Anonymous"
    if check_user_banned(message.from_user.id):
        BANNED_USERS.add(message.from_user.id)
        send_message(client, True, message.from_user.id, YOU_ARE_BANNED)
    else:
        if message.from_user.id not in itertools.chain(*get_users()):
            logging.warning(f"New user detected ({message.from_user.id}), adding to database")
            set_user(message.from_user.id, message.from_user.username)
        if GREET:
            send_message(client,
                         True,
                         message.from_user.id,
                         GREET.format(mention=f"[{name}](tg://user?id={message.from_user.id})",
                                      id=message.from_user.id,
                                       username=message.from_user.username
                                      ),
                         reply_markup=BUTTONS
                         )


@Client.on_callback_query(Filters.callback_data("info") & ~BANNED_USERS)
def bot_info(_, query):
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", "back_start")]])
    edit_message_text(query, True, CREDITS.format(), reply_markup=buttons)


@Client.on_callback_query(Filters.callback_data("back_start") & ~BANNED_USERS)
def back_start(_, query):
    if query.from_user.first_name:
        name = query.from_user.first_name
    elif query.from_user.username:
        name = query.from_user.username
    else:
        name = "Anonymous"
    if CACHE[query.from_user.id][0] == "AWAITING_ADMIN":
        data = CACHE[query.from_user.id][-1]
        if isinstance(data, list):
            for chatid, message_ids in data:
                delete_messages(_, True, chatid, message_ids)
    edit_message_text(query, True,
                      GREET.format(mention=f"[{name}](tg://user?id={query.from_user.id})", id=query.from_user.id,
                                   username=query.from_user.username),
                      reply_markup=BUTTONS)
