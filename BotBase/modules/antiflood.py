from pyrogram import Client, Filters, Message
from ..config import MAX_UPDATE_THRESHOLD, ANTIFLOOD_SENSIBILITY, BAN_TIME, ADMINS, BYPASS_FLOOD, FLOOD_NOTICE, \
    COUNT_CALLBACKS_SEPARATELY, FLOOD_PERCENTAGE, CACHE, PRIVATE_ONLY
from collections import defaultdict
import logging
import time
from ..methods.safe_send import send_message

# Some variables for runtime configuration

MESSAGES = defaultdict(list)  # Internal variable for the antiflood module
BANNED_USERS = Filters.user()  # Filters where the antiflood will put banned users
BYPASS_USERS = Filters.user(list(ADMINS.keys())) if BYPASS_FLOOD else Filters.user()
QUERIES = defaultdict(list) if COUNT_CALLBACKS_SEPARATELY else MESSAGES
FILTER = Filters.private if PRIVATE_ONLY else ~Filters.user()


def is_flood(updates: list):
    """Calculates if a sequence of
    updates corresponds to a flood"""

    genexpr = [i <= ANTIFLOOD_SENSIBILITY for i in
               ((updates[i + 1] - timestamp) if i < (MAX_UPDATE_THRESHOLD - 1) else (timestamp - updates[i - 1]) for
                i, timestamp in enumerate(updates))]
    limit = (len(genexpr) / 100) * FLOOD_PERCENTAGE
    if genexpr.count(True) >= limit:
        return True
    else:
        return False


@Client.on_callback_query(~BYPASS_USERS, group=-1)
@Client.on_message(FILTER & ~BYPASS_USERS, group=-1)
def anti_flood(client, update):
    """Anti flood module"""

    VAR = MESSAGES if isinstance(update, Message) else QUERIES
    if isinstance(VAR[update.from_user.id], tuple):
        chat, date = VAR[update.from_user.id]
        if time.time() - date >= BAN_TIME:
            logging.warning(f"{update.from_user.id} has waited at least {BAN_TIME} seconds and can now text again")
            BANNED_USERS.remove(update.from_user.id)
            del VAR[update.from_user.id]
    elif len(VAR[update.from_user.id]) >= MAX_UPDATE_THRESHOLD:
        logging.info(f"MAX_MESS_THRESHOLD ({MAX_UPDATE_THRESHOLD}) Reached for {update.from_user.id}")
        timestamps = VAR.pop(update.from_user.id)
        if is_flood(timestamps):
            logging.warning(f"Flood detected from {update.from_user.id} in chat {update.chat.id}")
            if update.from_user.id in CACHE:
                del CACHE[update.from_user.id]
            BANNED_USERS.add(update.from_user.id)
            if isinstance(update, Message):
                chatid = update.chat.id
            else:
                chatid = update.from_user.id
            VAR[update.from_user.id] = chatid, time.monotonic()
            if FLOOD_NOTICE:
                send_message(client, update.from_user.id, FLOOD_NOTICE)
        else:
            if update.from_user.id in VAR:
                del VAR[update.from_user.id]
    else:
        if isinstance(update, Message):
            date = update.date
        else:
            if update.message:
                date = update.message.date
            else:
                date = time.monotonic()
        VAR[update.from_user.id].append(date)
