# BotBase - Methods overview

BotBase has a builtin wrapper around Pyrogram methods objects that make
it even easier to use them properly.

**DISCLAIMER**: The ``MethodWrapper`` class is just a wrapper around Pyrogram. 


To use the "safe" methods, just import the `MethodWrapper` class from `BotBase.methods`
and pass it a `pyrogram.Client` **instance** (not the class) or a `pyrogram.CallbackQuery`
or even a `pyrogram.InlineQuery` object. Then you can just call `wrapper.method` rather than `client.method`.

This way, the calls will never trigger exceptions and will log errors to stderr.
If an exception occurs, the exception object is returned, otherwise whatever
the called pyrogram method returns will be returned.
