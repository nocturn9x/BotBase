from ..config import ADMINS, USER_INFO, INVALID_SYNTAX, ERROR, NONNUMERIC_ID, USERS_COUNT, \
    NO_PARAMETERS, ID_MISSING, GLOBAL_MESSAGE_STATS
from pyrogram import Client, Filters
from ..database.query import get_user, get_users
from .antiflood import BANNED_USERS
import random
from ..methods.safe_send import send_message
import logging


ADMINS_FILTER = Filters.user(list(ADMINS.keys()))


@Client.on_message(Filters.command("count") & ADMINS_FILTER & Filters.private & ~BANNED_USERS)
def count_users(client, message):
    logging.warning(f"Admin with id {message.from_user.id} sent /count")
    count = len(get_users())
    send_message(client, message.chat.id, USERS_COUNT.format(count))


@Client.on_message(Filters.command("getuser") & ADMINS_FILTER & Filters.private & ~BANNED_USERS)
def get_user_info(client, message):
    if len(message.command) == 2:
        if message.command[1].isdigit():
            user = get_user(message.command[1])
            if user:
                logging.warning(f"Admin with id {message.from_user.id} sent /getuser {message.command[1]}")
                _, uid, uname, date, banned = user
                text = USER_INFO.format(uid=uid, uname='@' + uname if uname != 'null' else uname, date=date, status='User' if not admin else 'Admin')
                send_message(client, message.chat.id, text)
            else:
                send_message(client, message.chat.id, f"{ERROR}: {ID_MISSING.format(uid=message.command[1])}")
        else:
            send_message(client, message.chat.id, f"{ERROR}: {NONNUMERIC_ID}")
    else:
        send_message(client, message.chat.id,  f"{INVALID_SYNTAX}: Use <code>/getuser user_id</code>")


@Client.on_message(Filters.command("getranduser") & ADMINS_FILTER & Filters.private & ~BANNED_USERS)
def get_random_user(client, message):
    logging.warning(f"Admin with id {message.from_user.id} sent /getranduser")
    if len(message.command) > 1:
        send_message(client, message.chat.id, f"{INVALID_SYNTAX}: {NO_PARAMETERS.format(command='/getranduser')}")
    else:
        user = random.choice(get_users())
        rowid, uid, uname, date, admin = get_user(*user)
        text = USER_INFO.format(uid=uid, uname='@' + uname if uname != 'null' else uname, date=date,
                                status='User' if not admin else 'Admin',
                                )
        send_message(client, message.chat.id, text)


@Client.on_message(Filters.command("global") & ADMINS_FILTER & Filters.private & ~BANNED_USERS)
def global_message(client, message):
    if len(message.command) > 1:
        msg = message.text.html[7:]
        logging.warning(f"Admin with id {message.from_user.id} sent the following global message: {msg}")
        missed = 0
        count = 0
        for uid in get_users():
            count += 1
            if not send_message(client, *uid, msg):    # Returns False if an error gets raised
                missed += 1
        send_message(client, message.chat.id, GLOBAL_MESSAGE_STATS.format(count=count, success=(count - missed), msg=msg))
    else:
        send_message(client, message.chat.id, f"{INVALID_SYNTAX}: Use <code>/global message</code>"
                                              "\n🍮 Note that the <code>/global</code> command supports markdown and html styling")
