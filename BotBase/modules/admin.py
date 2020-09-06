from ..config import ADMINS, USER_INFO, INVALID_SYNTAX, ERROR, NONNUMERIC_ID, USERS_COUNT, \
    NO_PARAMETERS, ID_MISSING, GLOBAL_MESSAGE_STATS, NAME, WHISPER_FROM, USER_INFO_UPDATED, USER_INFO_UNCHANGED, \
    USER_BANNED, USER_UNBANNED, CANNOT_BAN_ADMIN, USER_ALREADY_BANNED, USER_NOT_BANNED, YOU_ARE_BANNED, YOU_ARE_UNBANNED, \
    MARKED_BUSY, UNMARKED_BUSY, CACHE, YES, NO, NAME_MISSING, bot, WHISPER_SUCCESSFUL, LEAVE_CURRENT_CHAT, \
    QUEUE_LIST, CHATS_LIST, ADMIN_BUSY
from pyrogram import Client, Filters
from ..database.query import get_user, get_users, update_name, ban_user, unban_user, get_user_by_name
from .antiflood import BANNED_USERS
import random
import logging
import itertools
import re
from ..methods import MethodWrapper


ADMINS_FILTER = Filters.user(list(ADMINS.keys()))
wrapper = MethodWrapper(bot)

@Client.on_message(Filters.command("getranduser") & ADMINS_FILTER & ~BANNED_USERS & ~Filters.edited)
def get_random_user(client, message):
    logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /getranduser")
    if len(message.command) > 1:
        wrapper.send_message(message.chat.id, f"{NO_PARAMETERS.format(command='/getranduser')}")
    else:
        user = random.choice(get_users())
        rowid, uid, uname, date, banned = get_user(*user)
        admin = uid in ADMINS
        text = USER_INFO.format(uid=uid,
                                uname='@' + uname if uname else 'null',
                                date=date,
                                status=YES if banned else NO,
                                admin=NO if not admin else YES)
        wrapper.send_message(message.chat.id, text)


@Client.on_message(Filters.command("count") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def count_users(client, message):
    if len(message.command) > 1:
        wrapper.send_message(message.chat.id, f"{NO_PARAMETERS.format(command='/getranduser')}")
    else:
        logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /count")
        count = len(get_users())
        wrapper.send_message(message.chat.id, USERS_COUNT.format(count=count))


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
                                        uname='@' + uname if uname else 'null',
                                        date=date,
                                        status=YES if banned else NO,
                                        admin=NO if not admin else YES)
                wrapper.send_message(message.chat.id, text)
            else:
                wrapper.send_message(message.chat.id, f"{ERROR}: {ID_MISSING.format(uid=message.command[1])}")
        else:
            wrapper.send_message(message.chat.id, f"{ERROR}: {NONNUMERIC_ID}")
    else:
        wrapper.send_message(message.chat.id,  f"{INVALID_SYNTAX.format(correct='/getuser id')}")


@Client.on_message(Filters.command("userbyname") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def get_user_by_uname(client, message):
    if len(message.command) == 2:
        name = message.command[1].lstrip("@").lower()
        user = get_user_by_name(name)
        if user:
            logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /userbyname {message.command[1]}")
            _, uid, uname, date, banned = user
            admin = uid in ADMINS
            text = USER_INFO.format(uid=uid,
                                    uname='@' + uname if uname else 'null',
                                    date=date,
                                    status=YES if banned else NO,
                                    admin=NO if not admin else YES)
            wrapper.send_message(message.chat.id, text)
        else:
            wrapper.send_message(message.chat.id, f"{ERROR}: {NAME_MISSING.format(uname=message.command[1])}")
    else:
        wrapper.send_message(message.chat.id,  f"{INVALID_SYNTAX.format(correct='/userbyname [@]username')}")


@Client.on_message(Filters.command("global") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def global_message(client, message):
    if len(message.command) > 1:
        msg = message.text.html[7:]
        logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent the following global message: {msg}")
        missed = 0
        count = 0
        for uid in itertools.chain(*get_users()):
            count += 1
            result = wrapper.send_message( uid, msg)
            if isinstance(result, Exception):
                logging.error(f"Could not deliver the global message to {uid} because of {type(result).__name__}: {result}")
                missed += 1
        logging.warning(f"{count - missed}/{count} global messages were successfully delivered")
        wrapper.send_message(message.chat.id, GLOBAL_MESSAGE_STATS.format(count=count, success=(count - missed), msg=msg))
    else:
        wrapper.send_message(message.chat.id, f"{INVALID_SYNTAX.format(correct='/global message')}\n**HTML and Markdown styling supported**")


@Client.on_message(Filters.command("whisper") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def whisper(client, message):
    if len(message.command) > 2:
        msg = message.text.html[9:]
        logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent {message.text.html}")
        if message.command[1].isdigit():
            msg = msg[re.search(message.command[1], msg).end():]
            uid = int(message.command[1])
            if uid in itertools.chain(*get_users()):
                result = wrapper.send_message(uid, WHISPER_FROM.format(admin=f"[{ADMINS[message.from_user.id]}]({NAME.format(message.from_user.id)})",
                                                                       msg=msg)
                                              )
                if isinstance(result, Exception):
                    logging.error(
                        f"Could not whisper to {uid} because of {type(result).__name__}: {result}")
                    wrapper.send_message(message.chat.id, f"{ERROR}: {type(result).__name__} -> {result}")
                else:
                    wrapper.send_message(message.chat.id, WHISPER_SUCCESSFUL)
            else:
                wrapper.send_message(message.chat.id, f"{ERROR}: {ID_MISSING.format(uid=uid)}")
        else:
            wrapper.send_message(message.chat.id, f"{ERROR}: {NONNUMERIC_ID}")
    else:
        wrapper.send_message(message.chat.id, f"{INVALID_SYNTAX.format(correct='/whisper ID')}\n**HTML and Markdown styling supported**")


@Client.on_message(Filters.command("update") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def update(client, message):
    if len(message.command) == 2:
        if message.command[1].isdigit():
            user = get_user(message.command[1])
            if user:
                logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /update {message.command[1]}")
                _, uid, uname, date, banned = user
                new = wrapper.get_users(uid)
                if isinstance(new, Exception):
                    logging.error(f"An error has occurred when calling get_users({uid}), {type(new).__name__}: {new}")
                    wrapper.send_message(message.chat.id, f"{ERROR}: {type(new).__name__} -> {new}")
                else:
                    if new.username is None:
                        new.username = "null"
                    if new.username != uname:
                        update_name(uid, new.username)
                        wrapper.send_message(message.chat.id, USER_INFO_UPDATED)
                    else:
                        wrapper.send_message(message.chat.id, USER_INFO_UNCHANGED)
            else:
                wrapper.send_message(message.chat.id, f"{ERROR}: {ID_MISSING.format(uid=message.command[1])}")
        else:
            wrapper.send_message(message.chat.id, f"{ERROR}: {NONNUMERIC_ID}")
    else:
        wrapper.send_message(message.chat.id, f"{INVALID_SYNTAX.format(correct='/update ID')}")


@Client.on_message(Filters.command("ban") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def ban(client, message):
    if len(message.command) == 2:
        if message.command[1].isdigit():
            if int(message.command[1]) in ADMINS:
                wrapper.send_message(message.chat.id, CANNOT_BAN_ADMIN)
            else:
                user = get_user(message.command[1])
                if user:
                    if not user[-1]:
                        logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /ban {message.command[1]}")
                        _, uid, uname, date, banned = user
                        res = ban_user(int(message.command[1]))
                        if isinstance(res, Exception):
                            logging.error(f"An error has occurred when calling ban_user({uid}), {type(res).__name__}: {res}")
                            wrapper.send_message(message.chat.id, f"{ERROR}: {type(res).__name__} -> {res}")
                        else:
                            wrapper.send_message(message.chat.id, USER_BANNED)
                            wrapper.send_message( uid, YOU_ARE_BANNED)
                            BANNED_USERS.add(uid)
                    else:
                        wrapper.send_message(message.chat.id, USER_ALREADY_BANNED)
                else:
                    wrapper.send_message(message.chat.id, f"{ERROR}: {ID_MISSING.format(uid=message.command[1])}")
        else:
            wrapper.send_message(message.chat.id, f"{ERROR}: {NONNUMERIC_ID}")
    else:
        wrapper.send_message(message.chat.id,  f"{INVALID_SYNTAX.format(correct='/ban ID')}")


@Client.on_message(Filters.command("unban") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def unban(client, message):
    if len(message.command) == 2:
        if message.command[1].isdigit():
            if int(message.command[1]) in ADMINS:
                wrapper.send_message(message.chat.id, CANNOT_BAN_ADMIN)
            else:
                user = get_user(message.command[1])
                if user:
                    if user[-1]:
                        logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /unban {message.command[1]}")
                        _, uid, uname, date, banned = user
                        res = unban_user(int(message.command[1]))
                        if isinstance(res, Exception):
                            logging.error(f"An error has occurred when calling unban_user({uid}), {type(res).__name__}: {res}")
                            wrapper.send_message(message.chat.id, f"{ERROR}: {type(res).__name__} -> {res}")
                        else:
                            wrapper.send_message(message.chat.id, USER_UNBANNED)
                            if uid in BANNED_USERS:
                                BANNED_USERS.remove(uid)
                            wrapper.send_message( uid, YOU_ARE_UNBANNED)
                    else:
                        wrapper.send_message(message.chat.id, USER_NOT_BANNED)
                else:
                    wrapper.send_message(message.chat.id, f"{ERROR}: {ID_MISSING.format(uid=message.command[1])}")
        else:
            wrapper.send_message(message.chat.id, f"{ERROR}: {NONNUMERIC_ID}")
    else:
        wrapper.send_message(message.chat.id,  f"{INVALID_SYNTAX.format(correct='/unban ID')}")


@Client.on_message(Filters.command("busy") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def busy(client, message):
    logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /busy")
    if len(message.command) > 1:
        wrapper.send_message(message.chat.id, f"{NO_PARAMETERS.format(command='/busy')}")
    else:
        if CACHE[message.from_user.id][0] == "IN_CHAT" and CACHE[message.from_user.id][1] != 1234567:
            wrapper.send_message(message.from_user.id, LEAVE_CURRENT_CHAT)
        elif CACHE[message.from_user.id][0] == "none":
            wrapper.send_message(message.chat.id, MARKED_BUSY)
            CACHE[message.from_user.id] = ["IN_CHAT", 1234567]
        else:
            if message.from_user.id in CACHE:
                del CACHE[message.from_user.id]
            wrapper.send_message(message.chat.id, UNMARKED_BUSY)


@Client.on_message(Filters.command("chats") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def chats(client, message):
    logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /chats")
    if len(message.command) > 1:
        wrapper.send_message(message.chat.id, f"{NO_PARAMETERS.format(command='/chats')}")
    else:
        text = ""
        for user in CACHE:
            if CACHE[user][0] == "IN_CHAT" and user not in ADMINS:
                admin_id = CACHE[user][1]
                admin_name = ADMINS[admin_id]
                text += f"- 👤 [User]({NAME.format(user)}) -> 👨‍💻 [{admin_name}]({NAME.format(admin_id)})\n"
        wrapper.send_message(message.chat.id, CHATS_LIST.format(chats=text))

@Client.on_message(Filters.command("queue") & ADMINS_FILTER & Filters.private & ~BANNED_USERS & ~Filters.edited)
def queue(client, message):
    logging.warning(f"{ADMINS[message.from_user.id]} [{message.from_user.id}] sent /queue")
    if len(message.command) > 1:
        wrapper.send_message(message.chat.id, f"{NO_PARAMETERS.format(command='/queue')}")
    else:
        text = ""
        for user in CACHE:
            if CACHE[user][0] == "AWAITING_ADMIN":
                text += f"- 👤 [User]({NAME.format(user)})\n"
        wrapper.send_message(message.chat.id, QUEUE_LIST.format(queue=text))
