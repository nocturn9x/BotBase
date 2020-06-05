# BotBase - Methods overview

BotBase has a builtin collection of wrappers around Pyrogram methods that make
it even easier to use them properly.

**DISCLAIMER**: These methods are just wrappers around Pyrogram's ones and behave
exactly the same. Every method listed here takes 2 extra positional arguments,
namely a `Client`/`CallbackQuery` instance and a boolean parameter (read below)

All other arguments, including keyword ones, are passed to pyrogram directly.

The methods are wrapped in try/except blocks and log automatically all errors
to the console. Also, if `sleep=True` (which is by default) if the method raises
a `FloodWait` exception, the wrapper will sleep the required amount of time and
then return the `FloodWait` exception. If `sleep=False` the exception is returned
immediately. All other exceptions are catched under `RPCError` and are returned
if they get raised, too. If no exception occurs the wrapper will return whatever
the corresponding pyrogram method returns.

## Methods - Safe send

List of the available functions in `BotBase.methods.safe_send`

- `send_message`
- `send_photo`
- `send_audio`
- `send_animation`
- `send_sticker`

These are the exact names that pyrogram uses, to see their docs refer to
[pyrogram docs](https://docs.pyrogram.org/api/methods/)

## Methods - Safe edit

List of the available functions in `BotBase.methods.safe_edit`

- `edit_message_text`
- `edit_message_media`
- `edit_message_caption`

## Methods - Various

List of the available functions in `BotBase.methods.various`

- `answer` (for `CallbackQuery` objects)
- `delete_messages`

