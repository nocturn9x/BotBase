# BotBase - Methods overview

BotBase has a builtin collection of wrappers around Pyrogram methods that make
it even easier to use them properly.

**DISCLAIMER**: These methods are just wrappers around Pyrogram's ones and behave
the same way.


To use the "safe" methods, just import the `MethodWrapper`` class from `BotBase.methods`
and pass it a `pyrogram.Client` **instance** (not the class) or a `pyrogram.CallbackQuery`
or even a `pyrogram.InlineQuery` object. Then you can just call `wrapper.method` rather than `client.method`.

This way, the calls will never trigger exceptions and will log errors to stderr.
If an exception occurs, the exception object is returned, otherwise whatever
the called pyrogram method returns will be returned.
