from ..config import ADMINS, USER_INFO, INVALID_SYNTAX, ERROR, NONNUMERIC_ID, USERS_COUNT, \
    NO_PARAMETERS, ID_MISSING, GLOBAL_MESSAGE_STATS, NAME, WHISPER_FROM, USER_INFO_UPDATED, USER_INFO_UNCHANGED, \
    USER_BANNED, USER_UNBANNED, CANNOT_BAN_ADMIN, USER_ALREADY_BANNED, USER_NOT_BANNED, YOU_ARE_BANNED, YOU_ARE_UNBANNED, \
    MARKED_BUSY, UNMARKED_BUSY, CACHE
from pyrogram import Client, Filters
from ..database.query import get_user, get_users, update_name, ban_user, unban_user
from .antiflood import BANNED_USERS
import random
from ..methods.safe_send import send_message
from ..methods.various import get_users as get_telegram_users
import logging
import itertools
import re


ADMINS_FILTER = Filters.user(list(ADMINS.keys()))


@Client.on_message(Filters.command("count") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def count_users(client, message):
    logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /count")
    count = len(get_users())
    send_message(client, True, message.chat.id, USERS_COUNT.format(count=count))


@Client.on_message(Filters.command("getuser") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def get_user_info(client, message):
    if len(message.command) == 2:
        if message.command[1].isdigit():
            user = get_user(message.command[1])
            if user:
                logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /getuser {message.command[1]}")
                _, uid, uname, date, banned = user
                admin = uid in ADMINS
                text = USER_INFO.format(uid=uid,
                                        uname='@' + uname if uname != 'null' else uname,
                                        date=date,
                                        status='✅' if banned else '❌',
                                        admin='❌' if not admin else '✅')
                send_message(client, True, message.chat.id, text)
            else:
                send_message(client, True, message.chat.id, f"{ERROR}: {ID_MISSING.format(uid=message.command[1])}")
        else:
            send_message(client, True, message.chat.id, f"{ERROR}: {NONNUMERIC_ID}")
    else:
        send_message(client, True, message.chat.id,  f"{INVALID_SYNTAX}: Use <code>/getuser user_id</code>")


@Client.on_message(Filters.command("getranduser") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def get_random_user(client, message):
    logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /getranduser")
    if len(message.command) > 1:
        send_message(client, True, message.chat.id, f"{INVALID_SYNTAX}: {NO_PARAMETERS.format(command='/getranduser')}")
    else:
        user = random.choice(get_users())
        rowid, uid, uname, date, banned = get_user(*user)
        admin = uid in ADMINS
        text = USER_INFO.format(uid=uid,
                                uname='@' + uname if uname != 'null' else uname,
                                date=date,
                                status='✅' if banned else '❌',
                                admin='❌' if not admin else '✅')
        send_message(client, True, message.chat.id, text)


@Client.on_message(Filters.command("global") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def global_message(client, message):
    if len(message.command) > 1:
        msg = message.text.html[7:]
        logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent the following global message: {msg}")
        missed = 0
        count = 0
        for uid in itertools.chain(*get_users()):
            count += 1
            result = send_message(client, True, uid, msg)
            if isinstance(result, Exception):
                logging.error(f"Could not deliver the global message to {uid} because of {type(result).__name__}: {result}")
                missed += 1
        logging.warning(f"{count - missed}/{count} global messages were successfully delivered")
        send_message(client, True, message.chat.id, GLOBAL_MESSAGE_STATS.format(count=count, success=(count - missed), msg=msg))
    else:
        send_message(client, True, message.chat.id, f"{INVALID_SYNTAX}: Use <code>/global message</code>"
                     f"\n🍮 Note that the <code>/global</code> command supports markdown and html styling")


@Client.on_message(Filters.command("whisper") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def whisper(client, message):
    if len(message.command) > 2:
        msg = message.text.html[9:]
        logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent {message.text.html}")
        if message.command[1].isdigit():
            msg = msg[re.search(message.command[1], msg).end():]
            uid = int(message.command[1])
            if uid in itertools.chain(*get_users()):
                result = send_message(client, True, uid, WHISPER_FROM.format(admin=f"[{ADMINS[message.from_user.id]}]({NAME.format(message.from_user.id)})",
                                                                             msg=msg)
                                      )
                if isinstance(result, Exception):
                    logging.error(
                        f"Could not whisper to {uid} because of {type(result).__name__}: {result}")
                    send_message(client, True, message.chat.id, f"{ERROR}: {type(result).__name__} -> {result}")
            else:
                send_message(client, True, message.chat.id, f"{ERROR}: {ID_MISSING.format(uid=uid)}")
        else:
            send_message(client, True, message.chat.id, f"{ERROR}: {NONNUMERIC_ID}")
    else:
        send_message(client, True, message.chat.id, f"{INVALID_SYNTAX}: Use <code>/whisper ID message</code>"
        f"\n🍮 Note that the <code>/whisper</code> command supports markdown and html styling")


@Client.on_message(Filters.command("update") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def update(client, message):
    if len(message.command) == 2:
        if message.command[1].isdigit():
            user = get_user(message.command[1])
            if user:
                logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /update {message.command[1]}")
                _, uid, uname, date, banned = user
                new = get_telegram_users(client, True, uid)
                if isinstance(new, Exception):
                    logging.error(f"An error has occurred when calling get_users({uid}), {type(new).__name__}: {new}")
                    send_message(client, True, message.chat.id, f"{ERROR}: {type(new).__name__} -> {new}")
                else:
                    if new.username is None:
                        new.username = "null"
                    if new.username != uname:
                        update_name(uid, new.username)
                        send_message(client, True, message.chat.id, USER_INFO_UPDATED)
                    else:
                        send_message(client, True, message.chat.id, USER_INFO_UNCHANGED)
            else:
                send_message(client, True, message.chat.id, f"{ERROR}: {ID_MISSING.format(uid=message.command[1])}")
        else:
            send_message(client, True, message.chat.id, f"{ERROR}: {NONNUMERIC_ID}")
    else:
        send_message(client, True, message.chat.id,  f"{INVALID_SYNTAX}: Use <code>/update user_id</code>")


@Client.on_message(Filters.command("ban") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def ban(client, message):
    if len(message.command) == 2:
        if message.command[1].isdigit():
            if int(message.command[1]) in ADMINS:
                send_message(client, True, message.chat.id, CANNOT_BAN_ADMIN)
            else:
                user = get_user(message.command[1])
                if user:
                    if not user[-1]:
                        logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /ban {message.command[1]}")
                        _, uid, uname, date, banned = user
                        res = ban_user(int(message.command[1]))
                        if isinstance(res, Exception):
                            logging.error(f"An error has occurred when calling ban_user({uid}), {type(res).__name__}: {res}")
                            send_message(client, True, message.chat.id, f"{ERROR}: {type(res).__name__} -> {res}")
                        else:
                            send_message(client, True, message.chat.id, USER_BANNED)
                            send_message(client, True, uid, YOU_ARE_BANNED)
                            BANNED_USERS.add(uid)
                    else:
                        send_message(client, True, message.chat.id, USER_ALREADY_BANNED)
                else:
                    send_message(client, True, message.chat.id, f"{ERROR}: {ID_MISSING.format(uid=message.command[1])}")
        else:
            send_message(client, True, message.chat.id, f"{ERROR}: {NONNUMERIC_ID}")
    else:
        send_message(client, True, message.chat.id,  f"{INVALID_SYNTAX}: Use <code>/ban user_id</code>")


@Client.on_message(Filters.command("unban") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def unban(client, message):
    if len(message.command) == 2:
        if message.command[1].isdigit():
            if int(message.command[1]) in ADMINS:
                send_message(client, True, message.chat.id, CANNOT_BAN_ADMIN)
            else:
                user = get_user(message.command[1])
                if user:
                    if user[-1]:
                        logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /unban {message.command[1]}")
                        _, uid, uname, date, banned = user
                        res = unban_user(int(message.command[1]))
                        if isinstance(res, Exception):
                            logging.error(f"An error has occurred when calling unban_user({uid}), {type(res).__name__}: {res}")
                            send_message(client, True, message.chat.id, f"{ERROR}: {type(res).__name__} -> {res}")
                        else:
                            send_message(client, True, message.chat.id, USER_UNBANNED)
                            if uid in BANNED_USERS:
                                BANNED_USERS.remove(uid)
                            send_message(client, True, uid, YOU_ARE_UNBANNED)
                    else:
                        send_message(client, True, message.chat.id, USER_NOT_BANNED)
                else:
                    send_message(client, True, message.chat.id, f"{ERROR}: {ID_MISSING.format(uid=message.command[1])}")
        else:
            send_message(client, True, message.chat.id, f"{ERROR}: {NONNUMERIC_ID}")
    else:
        send_message(client, True, message.chat.id,  f"{INVALID_SYNTAX}: Use <code>/unban user_id</code>")


@Client.on_message(Filters.command("/busy") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def get_random_user(client, message):
    logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /busy")
    if len(message.command) > 1:
        send_message(client, True, message.chat.id, f"{INVALID_SYNTAX}: {NO_PARAMETERS.format(command='/busy')}")
    else:
        if CACHE[message.from_user.id][0] == "none":
            send_message(client, True, message.chat.id, MARKED_BUSY)
            CACHE[message.from_user.id] = ["IN_CHAT", 1234567]
        else:
            if message.from_user.id in CACHE:
                del CACHE[message.from_user.id]
            send_message(client, True, message.chat.id, UNMARKED_BUSY)
