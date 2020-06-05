# BotBase - Notes on database interaction

BotBase has an built-in API to interact with a SQLite3 database, located in the
`BotBase/database/query.py` module. The reason why SQLite3 was chosen among the
lots of options is that it's lightweight, has less security concerns (no user
and password to remember) and requires literally no setup at all.

The configuration is hassle-free, you can keep the default values and they'll
work just fine. If you need a more complex database structure, just edit
the `DB_CREATE` SQL query to fit your needs, but do not alter the default
`users` table unless you also change all the SQL queries in the `config.py`
file as this would otherwise break the whole internal machinery of BotBase.

## Available methods

The module `BotBase.database.query` implements the following default methods
to interact with the database. All methods either return the result of a query
or `True` if the operation was successful, or an exception if the query errored.

Please note that the methods are **NOT** locked and that proper locking is
needed if you think that your bot might get a `sqlite3.OoerationalError: database
is locked` error when accessing the database.

All queries are performed within a `with` block and therefore rollbacked
automatically if an error occurs or committed if the transaction was successful.

    - `get_user()` -> Given a Telegram ID as input, returns a tuple containing
    the unique id of the user in the database, its telegram id, username,
    the date and time the user was inserted in the database as a string
    (formatted as d/m/Y H:M:S) and an integer (0 for `False` and 1 for `True`)
    that represents the user's status (whether it is banned or not)

    - `get_users()` -> This acts similarly to the above `get_user`, but takes
    no parameters and returns a list of all the users in the database. The
    list contains tuples of the same structure of the ones returned by `get_user`

    - `set_user()` -> Saves an ID/username pair (in this order)
    to the database. The username parameter can be `None`

    - `ban_user()` -> Bans the user with the given user ID (Coming soon)

    - `unban_user()` -> Unbans a user with the given ID (Coming soon)

# I need MySQL/other DBMS!

The API has been designed in a way that makes it easy to swap between different
database managers, so if you feel in the right mood make a PR to support a new
database and it'll be reviewed ASAP.

