from pyrogram import Client, Filters, InlineKeyboardButton, InlineKeyboardMarkup
from .antiflood import BANNED_USERS
from ..config import GREET, BUTTONS, CREDITS
from ..database.query import get_users, set_user
import logging
import itertools
from ..methods.safe_send import send_message
from ..methods.safe_edit import edit_message_text


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
    if message.from_user.id not in itertools.chain(*get_users()):
        logging.warning(f"New user detected ({message.from_user.id}), adding to database")
        set_user(message.from_user.id, None if not message.from_user.username else message.from_user.username)
    send_message(client, message.chat.id, GREET.format(mention=f"[{name}](tg://user?id={message.from_user.id})"),
                 reply_markup=BUTTONS)


@Client.on_callback_query(Filters.callback_data("info"))
def bot_info(_, query):
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", "back_start")]])
    edit_message_text(query, CREDITS, reply_markup=buttons)