from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton
from ..methods.safe_send import send_message
from ..methods.safe_edit import edit_message_text
from ..methods.various import answer, delete_messages
from ..config import CACHE, ADMINS, ADMINS_LIST_UPDATE_DELAY, callback_regex, admin_is_chatting, \
    user_is_chatting, LIVE_CHAT_STATUSES, STATUS_BUSY, STATUS_FREE, SUPPORT_REQUEST_SENT, SUPPORT_NOTIFICATION, \
    ADMIN_JOINS_CHAT, USER_CLOSES_CHAT, JOIN_CHAT_BUTTON, USER_INFO, USER_LEAVES_CHAT, ADMIN_MESSAGE, USER_MESSAGE, \
    TOO_FAST, CHAT_BUSY, LEAVE_CURRENT_CHAT, USER_JOINS_CHAT, NAME
import time
from ..database.query import get_user
from .antiflood import BANNED_USERS
from .start import back_start
import logging


ADMINS_FILTER = Filters.user(list(ADMINS.keys()))
BUTTONS = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🔙 Back", "back_start")],
        [InlineKeyboardButton("🔄 Update", "update_admins_list")]
    ])


@Client.on_callback_query(Filters.callback_data("sos") & ~BANNED_USERS)
def begin_chat(client, query):
    CACHE[query.from_user.id] = ["AWAITING_ADMIN", time.time()]
    queue = LIVE_CHAT_STATUSES
    for admin_id, admin_name in ADMINS.items():
        status = CACHE[admin_id][0]
        if status != "IN_CHAT":
            queue += f"- {STATUS_FREE}"
        else:
            queue += f"- {STATUS_BUSY}"
        queue += f"[{admin_name}]({NAME.format(admin_id)})\n"
    msg = edit_message_text(query, True, SUPPORT_REQUEST_SENT.format(queue=queue, date=time.strftime('%d/%m/%Y %T')),
                            reply_markup=BUTTONS)
    join_chat_button = InlineKeyboardMarkup([[InlineKeyboardButton(JOIN_CHAT_BUTTON, f"join_{query.from_user.id}")]])
    user = get_user(query.from_user.id)
    _, uid, uname, date, banned = user
    admin = uid in ADMINS
    text = USER_INFO.format(uid=uid, uname='@' + uname if uname != 'null' else uname, date=date,
                            status='✅' if banned else '❌',
                            admin='❌' if not admin else '✅')
    CACHE[query.from_user.id].append([])
    for admin in ADMINS:
        status = CACHE[admin][0]
        if status != "IN_CHAT":
            message = send_message(client, True, admin, SUPPORT_NOTIFICATION.format(uinfo=text), reply_markup=join_chat_button)
            CACHE[query.from_user.id][-1].append((message.chat.id, message.message_id))
    CACHE[query.from_user.id][-1].append((msg.chat.id, msg.message_id))


@Client.on_callback_query(Filters.callback_data("update_admins_list") & ~BANNED_USERS)
def update_admins_list(_, query):
    if time.time() - CACHE[query.from_user.id][1] >= ADMINS_LIST_UPDATE_DELAY:
        if CACHE[query.from_user.id][0] == "AWAITING_ADMIN":
            CACHE[query.from_user.id] = ["AWAITING_ADMIN", time.time()]
            queue = LIVE_CHAT_STATUSES
            for admin_id, admin_name in ADMINS.items():
                status = CACHE[admin_id][0]
                if status != "IN_CHAT":
                    queue += f"- {STATUS_FREE}"
                else:
                    queue += f"- {STATUS_BUSY}"
                queue += f"[{admin_name}]({NAME.format(admin_id)})\n"
            edit_message_text(query, True, SUPPORT_REQUEST_SENT.format(queue=queue, date=time.strftime('%d/%m/%Y %T')),
                              reply_markup=BUTTONS)
        else:
            back_start(_, query)
    else:
        answer(query, True, TOO_FAST, show_alert=True)


@Client.on_callback_query(callback_regex(r"close_chat_\d+") & ~BANNED_USERS)
def close_chat(_, query):
    if user_is_chatting() or admin_is_chatting():
        user_id = int(query.data.split("_")[2])
        if query.from_user.id in ADMINS:
            data = CACHE[CACHE[query.from_user.id][1]][-1]
            if isinstance(data, list):
                data.append((query.from_user.id, query.message.message_id))
                for chatid, message_ids in data:
                    delete_messages(_, True, chatid, message_ids)
            status = CACHE[query.from_user.id][0]
            if status == "IN_CHAT":
                del CACHE[query.from_user.id][1]
                send_message(_, True, query.from_user.id, USER_LEAVES_CHAT)
                admin_id, admin_name = query.from_user.id, ADMINS[query.from_user.id]
                if CACHE[user_id][1]:
                    send_message(_, True, user_id,
                                 USER_CLOSES_CHAT.format(user_id=NAME.format(admin_id), user_name=admin_name))
                if user_id in CACHE:
                    del CACHE[user_id]
                logging.warning(f"{ADMINS[admin_id]} [{admin_id}] has terminated the chat with user {CACHE[admin_id][1]}")
                del CACHE[admin_id]
        else:
            data = CACHE[query.from_user.id][-1]
            if isinstance(data, list):
                for chatid, message_ids in data:
                    delete_messages(_, True, chatid, message_ids)
            admin_id = CACHE[query.from_user.id][1]
            if CACHE[user_id][1]:
                if query.from_user.first_name:
                    user_name = query.from_user.first_name
                elif query.from_user.username:
                    user_name = query.from_user.username
                else:
                    user_name = "Anonymous"
                logging.warning(f"{user_name} [{query.from_user.id}] has terminated the chat with admin {ADMINS[admin_id]} [{admin_id}]")
                send_message(_, True, query.from_user.id,
                             USER_LEAVES_CHAT)
                send_message(_, True, CACHE[user_id][1],
                             USER_CLOSES_CHAT.format(user_id=NAME.format(query.from_user.id), user_name=user_name))
                del CACHE[query.from_user.id]
                del CACHE[admin_id]
            else:
                back_start(_, query)


@Client.on_message(admin_is_chatting() & Filters.text & ~BANNED_USERS)
def forward_from_admin(client, message):
    logging.warning(f"Admin {ADMINS[message.from_user.id]} [{message.from_user.id}] says to {CACHE[message.from_user.id][1]}: {message.text.html}")
    send_message(client, True, CACHE[message.from_user.id][1],
                 ADMIN_MESSAGE.format(user_name=ADMINS[message.from_user.id],
                                      user_id=NAME.format(message.from_user.id),
                                      message=message.text.html))


@Client.on_message(user_is_chatting() & Filters.text & ~BANNED_USERS)
def forward_from_user(client, message):
    if message.from_user.first_name:
        name = message.from_user.first_name
    elif message.from_user.username:
        name = message.from_user.username
    else:
        name = "Anonymous"
    logging.warning(f"User {name} [{message.from_user.id}] says to Admin {ADMINS[CACHE[message.from_user.id][1]]} [{CACHE[message.from_user.id][1]}]: {message.text.html}")
    send_message(client, True, CACHE[message.from_user.id][1],
                 USER_MESSAGE.format(user_name=name, user_id=NAME.format(message.from_user.id),
                                     message=message.text.html))


@Client.on_callback_query(ADMINS_FILTER & callback_regex(r"join_\d+") & ~BANNED_USERS)
def join_chat(_, query):
    if CACHE[query.from_user.id][0] != "IN_CHAT":
        user_id = int(query.data.split("_")[1])
        if CACHE[user_id][0] != "AWAITING_ADMIN":
            answer(query, True, CHAT_BUSY)
        else:
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close chat", f"close_chat_{user_id}")]])
            admin_id, admin_name = query.from_user.id, ADMINS[query.from_user.id]
            CACHE[user_id] = ["IN_CHAT", admin_id, CACHE[user_id][-1]]
            CACHE[query.from_user.id] = ["IN_CHAT", user_id]
            message = send_message(_, True, query.from_user.id, USER_JOINS_CHAT, reply_markup=buttons)
            admin_joins = send_message(_, True, user_id, ADMIN_JOINS_CHAT.format(admin_name=admin_name, admin_id=NAME.format(admin_id)),
                                       reply_markup=buttons)
            for chatid, message_ids in CACHE[CACHE[query.from_user.id][1]][-1]:
                delete_messages(_, True, chatid, message_ids)
            CACHE[user_id][-1].append((message.chat.id, message.message_id))
            CACHE[user_id][-1].append((admin_joins.chat.id, admin_joins.message_id))
    else:
        answer(query, True, LEAVE_CURRENT_CHAT)
