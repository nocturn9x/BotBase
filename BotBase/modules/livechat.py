from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton
from ..config import CACHE, ADMINS, ADMINS_LIST_UPDATE_DELAY, callback_regex, admin_is_chatting, \
    user_is_chatting, LIVE_CHAT_STATUSES, STATUS_BUSY, STATUS_FREE, SUPPORT_REQUEST_SENT, SUPPORT_NOTIFICATION, \
    ADMIN_JOINS_CHAT, USER_CLOSES_CHAT, JOIN_CHAT_BUTTON, USER_INFO, USER_LEAVES_CHAT, ADMIN_MESSAGE, USER_MESSAGE, \
    TOO_FAST, CHAT_BUSY, LEAVE_CURRENT_CHAT, USER_JOINS_CHAT, NAME, CANNOT_REQUEST_SUPPORT, YES, NO, user_banned, CLOSE_CHAT_BUTTON, BACK_BUTTON, UPDATE_BUTTON, bot
import time
from ..database.query import get_user
from .antiflood import BANNED_USERS
from .start import back_start
import logging
from ..methods import MethodWrapper


ADMINS_FILTER = Filters.user(list(ADMINS.keys()))
BUTTONS = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(BACK_BUTTON, "back_start")],
        [InlineKeyboardButton(UPDATE_BUTTON, "update_admins_list")]
    ])
wrapper = MethodWrapper(bot)


@Client.on_callback_query(Filters.callback_data("sos") & ~BANNED_USERS & ~user_banned())
def begin_chat(client, query):
    cb_wrapper = MethodWrapper(query)
    if query.from_user.id in ADMINS:
        cb_wrapper.answer(CANNOT_REQUEST_SUPPORT)
    else:
        CACHE[query.from_user.id] = ["AWAITING_ADMIN", time.time()]
        queue = LIVE_CHAT_STATUSES
        for admin_id, admin_name in ADMINS.items():
            status = CACHE[admin_id][0]
            if status != "IN_CHAT":
                queue += f"- {STATUS_FREE}"
            else:
                queue += f"- {STATUS_BUSY}"
            queue += f"[{admin_name}]({NAME.format(admin_id)})\n"
        msg = cb_wrapper.edit_message_text(SUPPORT_REQUEST_SENT.format(queue=queue, date=time.strftime('%d/%m/%Y %T')),
                                        reply_markup=BUTTONS)
        join_chat_button = InlineKeyboardMarkup([[InlineKeyboardButton(JOIN_CHAT_BUTTON, f"join_{query.from_user.id}")]])
        user = get_user(query.from_user.id)
        _, uid, uname, date, banned = user
        text = USER_INFO.format(uid=uid, uname='@' + uname if uname else 'null', date=date,
                                status=YES if banned else NO,
                                admin='N/A')
        CACHE[query.from_user.id].append([])
        for admin in ADMINS:
            status = CACHE[admin][0]
            if status != "IN_CHAT":
                message = wrapper.send_message(admin, SUPPORT_NOTIFICATION.format(uinfo=text), reply_markup=join_chat_button)
                CACHE[query.from_user.id][-1].append((message.chat.id, message.message_id))
                CACHE[admin] = ["NOTIFICATION_SENT", query.from_user.id]
        CACHE[query.from_user.id][-1].append((msg.chat.id, msg.message_id))


@Client.on_callback_query(Filters.callback_data("update_admins_list") & ~BANNED_USERS & ~user_banned())
def update_admins_list(_, query):
    cb_wrapper = MethodWrapper(query)
    if CACHE[query.from_user.id][0] == "AWAITING_ADMIN":
        if time.time() - CACHE[query.from_user.id][1] >= ADMINS_LIST_UPDATE_DELAY:
            CACHE[query.from_user.id][1] = time.time()
            queue = LIVE_CHAT_STATUSES
            for admin_id, admin_name in ADMINS.items():
                status = CACHE[admin_id][0]
                if status != "IN_CHAT":
                    queue += f"- {STATUS_FREE}"
                else:
                    queue += f"- {STATUS_BUSY}"
                queue += f"[{admin_name}]({NAME.format(admin_id)})\n"
            cb_wrapper.edit_message_text(SUPPORT_REQUEST_SENT.format(queue=queue, date=time.strftime('%d/%m/%Y %T')),
                                         reply_markup=BUTTONS)
            join_chat_button = InlineKeyboardMarkup([[InlineKeyboardButton(JOIN_CHAT_BUTTON, f"join_{query.from_user.id}")]])
            user = get_user(query.from_user.id)
            _, uid, uname, date, banned = user
            text = USER_INFO.format(uid=uid, uname='@' + uname if uname else 'null', date=date,
                                    status=YES if banned else NO,
                                    admin='N/A')
            for admin in ADMINS:
                status = CACHE[admin][0]
                if status != "IN_CHAT":
                    if status != "NOTIFICATION_SENT" and CACHE[admin][1] != uid:
                        message = wrapper.send_message(admin, SUPPORT_NOTIFICATION.format(uinfo=text), reply_markup=join_chat_button)
                        CACHE[query.from_user.id][-1].append((message.chat.id, message.message_id))
        else:
            cb_wrapper.answer(TOO_FAST, show_alert=True)
    else:
        back_start(_, query)


@Client.on_callback_query(~user_banned() & callback_regex(r"close_chat_\d+") & ~BANNED_USERS & user_is_chatting() | admin_is_chatting() & ~BANNED_USERS & callback_regex(r"close_chat_\d+"))
def close_chat(_, query):
    user_id = int(query.data.split("_")[2])
    if query.from_user.id in ADMINS:
        data = CACHE[user_id][-1]
        if isinstance(data, list):
            data.append((query.from_user.id, query.message.message_id))
            for chatid, message_ids in data:
                wrapper.delete_messages(chatid, message_ids)
        status = CACHE[query.from_user.id][0]
        if status == "IN_CHAT":
            wrapper.send_message(query.from_user.id, USER_LEAVES_CHAT)
            admin_id, admin_name = query.from_user.id, ADMINS[query.from_user.id]
            logging.warning(f"{ADMINS[admin_id]} [{admin_id}] has terminated the chat with user {CACHE[admin_id][1]}")
            if CACHE[user_id][0] == "IN_CHAT":
                del CACHE[user_id]
                wrapper.send_message(user_id,
                             USER_CLOSES_CHAT.format(user_id=NAME.format(admin_id), user_name=admin_name))
            del CACHE[query.from_user.id]

    else:
        data = CACHE[query.from_user.id][-1]
        if isinstance(data, list):
            for chatid, message_ids in data:
                wrapper.delete_messages(chatid, message_ids)
        admin_id = CACHE[query.from_user.id][1]
        if CACHE[user_id][1]:
            if query.from_user.first_name:
                user_name = query.from_user.first_name
            elif query.from_user.username:
                user_name = query.from_user.username
            else:
                user_name = "Anonymous"
            logging.warning(f"{user_name} [{query.from_user.id}] has terminated the chat with admin {ADMINS[admin_id]} [{admin_id}]")
            wrapper.send_message(query.from_user.id,
                         USER_LEAVES_CHAT)
            wrapper.send_message(CACHE[user_id][1],
                         USER_CLOSES_CHAT.format(user_id=NAME.format(query.from_user.id), user_name=user_name))
            del CACHE[query.from_user.id]
            del CACHE[admin_id]
        else:
            back_start(_, query)


@Client.on_message(admin_is_chatting() & ~BANNED_USERS & ~user_banned())
def forward_from_admin(client, message):
    if message.text:
        logging.warning(f"Admin {ADMINS[message.from_user.id]} [{message.from_user.id}] says to {CACHE[message.from_user.id][1]}: {message.text.html}")
        wrapper.send_message(CACHE[message.from_user.id][1],
                             ADMIN_MESSAGE.format(user_name=ADMINS[message.from_user.id],
                                      user_id=NAME.format(message.from_user.id),
                                      message=message.text.html))
    elif message.photo:
        wrapper.send_photo(CACHE[message.from_user.id][1], photo=message.photo.file_id, file_ref=message.photo.file_ref, caption=ADMIN_MESSAGE.format(user_name=ADMINS[message.from_user.id], user_id=NAME.format(message.from_user.id), message=message.caption.html or '' if message.caption else '' if message.caption else ''))
    elif message.audio:
        wrapper.send_audio(CACHE[message.from_user.id][1], audio=message.audio.file_id, file_ref=message.audio.file_ref, caption=ADMIN_MESSAGE.format(user_name=ADMINS[message.from_user.id], user_id=NAME.format(message.from_user.id), message=message.caption.html or '' if message.caption else ''))
    elif message.document:
        wrapper.send_document(CACHE[message.from_user.id][1], document=message.document.file_id, file_ref=message.document.file_ref, caption=ADMIN_MESSAGE.format(user_name=ADMINS[message.from_user.id], user_id=NAME.format(message.from_user.id), message=message.caption.html or '' if message.caption else ''))
    elif message.sticker:
        wrapper.send_sticker(CACHE[message.from_user.id][1], sticker=message.sticker.file_id, file_ref=message.sticker.file_ref)
    elif message.video:
        wrapper.send_video(CACHE[message.from_user.id][1], video=message.video.file_id, file_ref=message.video.file_ref, caption=ADMIN_MESSAGE.format(user_name=ADMINS[message.from_user.id], user_id=NAME.format(message.from_user.id), message=message.caption.html or '' if message.caption else ''))
    elif message.animation:
        wrapper.send_animation(CACHE[message.from_user.id][1], animation=message.animation.file_id, file_ref=message.animation.file_ref, caption=ADMIN_MESSAGE.format(user_name=ADMINS[message.from_user.id], user_id=NAME.format(message.from_user.id), message=message.caption.html or '' if message.caption else ''))
    elif message.voice:
        wrapper.send_voice(CACHE[message.from_user.id][1], voice=message.voice.file_id, file_ref=message.voice.file_ref, caption=ADMIN_MESSAGE.format(user_name=ADMINS[message.from_user.id], user_id=NAME.format(message.from_user.id), message=message.caption.html or '' if message.caption else ''))
    elif message.video_note:
        wrapper.send_video_note(CACHE[message.from_user.id][1], video_note=message.video_note.file_id, file_ref=message.video_note.file_ref)
    elif message.location:
        wrapper.send_location(CACHE[message.from_user.id][1], latitude =message.location.latitude , longitude=message.location.longitude)
    elif message.contact:
        wrapper.send_contact(CACHE[message.from_user.id][1], phone_number=message.contact.phone_number, first_name=message.contact.first_name, last_name=message.contact.last_name)
    elif message.poll:
        wrapper.forward_messages(CACHE[message.from_user.id][1], from_chat_id=message.chat.id, message_ids=message.message_id, as_copy=False)


@Client.on_message(user_is_chatting() & ~BANNED_USERS & ~user_banned())
def forward_from_user(client, message):
    if message.from_user.first_name:
        name = message.from_user.first_name
    elif message.from_user.username:
        name = message.from_user.username
    else:
        name = "Anonymous"
    if message.text:
        logging.warning(f"User {name} [{message.from_user.id}] says to Admin {ADMINS[CACHE[message.from_user.id][1]]} [{CACHE[message.from_user.id][1]}]: {message.text.html}")
        wrapper.send_message(CACHE[message.from_user.id][1],
                 USER_MESSAGE.format(user_name=name, user_id=NAME.format(message.from_user.id),
                                     message=message.text.html))
    elif message.photo:
        wrapper.send_photo(CACHE[message.from_user.id][1], photo=message.photo.file_id, file_ref=message.photo.file_ref, caption=USER_MESSAGE.format(user_name=name, user_id=NAME.format(message.from_user.id), message=message.caption.html or '' if message.caption else ''))
    elif message.audio:
        wrapper.send_audio(CACHE[message.from_user.id][1], audio=message.audio.file_id, file_ref=message.audio.file_ref, caption=USER_MESSAGE.format(user_name=name, user_id=NAME.format(message.from_user.id), message=message.caption.html or '' if message.caption else ''))
    elif message.document:
        wrapper.send_document(CACHE[message.from_user.id][1], document=message.document.file_id, file_ref=message.document.file_ref, caption=USER_MESSAGE.format(user_name=name, user_id=NAME.format(message.from_user.id), message=message.caption.html or '' if message.caption else ''))
    elif message.sticker:
        wrapper.send_sticker(CACHE[message.from_user.id][1], sticker=message.sticker.file_id, file_ref=message.sticker.file_ref)
    elif message.video:
        wrapper.send_video(CACHE[message.from_user.id][1], video=message.video.file_id, file_ref=message.video.file_ref, caption=USER_MESSAGE.format(user_name=name, user_id=NAME.format(message.from_user.id), message=message.caption.html or '' if message.caption else ''))
    elif message.animation:
        wrapper.send_animation(CACHE[message.from_user.id][1], animation=message.animation.file_id, file_ref=message.animation.file_ref, caption=USER_MESSAGE.format(user_name=name, user_id=NAME.format(message.from_user.id), message=message.caption.html or '' if message.caption else ''))
    elif message.voice:
        wrapper.send_voice(CACHE[message.from_user.id][1], voice=message.voice.file_id, file_ref=message.voice.file_ref, caption=USER_MESSAGE.format(user_name=name, user_id=NAME.format(message.from_user.id), message=message.caption.html or '' if message.caption else ''))
    elif message.video_note:
        wrapper.send_video_note(CACHE[message.from_user.id][1], video_note=message.video_note.file_id, file_ref=message.video_note.file_ref)
    elif message.location:
        wrapper.send_location(CACHE[message.from_user.id][1], latitude =message.location.latitude , longitude=message.location.longitude)
    elif message.contact:
        wrapper.send_contact(CACHE[message.from_user.id][1], phone_number=message.contact.phone_number, first_name=message.contact.first_name, last_name=message.contact.last_name)
    elif message.poll:
        wrapper.forward_messages(CACHE[message.from_user.id][1], from_chat_id=message.chat.id, message_ids=message.message_id, as_copy=False)


@Client.on_callback_query(ADMINS_FILTER & callback_regex(r"join_\d+") & ~BANNED_USERS & ~user_banned())
def join_chat(_, query):
    cb_wrapper = MethodWrapper(query)
    if CACHE[query.from_user.id][0] != "IN_CHAT":
        user_id = int(query.data.split("_")[1])
        if CACHE[user_id][0] != "AWAITING_ADMIN":
            cb_wrapper.answer(CHAT_BUSY)
        else:
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton(CLOSE_CHAT_BUTTON, f"close_chat_{user_id}")]])
            admin_id, admin_name = query.from_user.id, ADMINS[query.from_user.id]
            CACHE[user_id] = ["IN_CHAT", admin_id, CACHE[user_id][-1]]
            CACHE[query.from_user.id] = ["IN_CHAT", user_id]
            message = wrapper.send_message(query.from_user.id, USER_JOINS_CHAT, reply_markup=buttons)
            admin_joins = wrapper.send_message(user_id, ADMIN_JOINS_CHAT.format(admin_name=admin_name, admin_id=NAME.format(admin_id)),
                                       reply_markup=buttons)
            for chatid, message_ids in CACHE[user_id][-1]:
                wrapper.delete_messages(chatid, message_ids)
            CACHE[user_id][-1].append((message.chat.id, message.message_id))
            CACHE[user_id][-1].append((admin_joins.chat.id, admin_joins.message_id))
    else:
        cb_wrapper.answer(LEAVE_CURRENT_CHAT)

