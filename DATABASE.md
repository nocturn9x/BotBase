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

- `get_users()` -> This method takes no parameter and returns a list
of tuples. Each tuple contains a user ID as stored in the database

- `set_user()` -> Saves an ID/username pair (in this order)
to the database. The username parameter can be `None`

- `ban_user()` -> Bans the user with the given user ID

- `unban_user()` -> Unbans a user with the given ID

- `update_user` -> Updates a user's username with the given ID

# I need MySQL/other DBMS!

The API has been designed in a way that makes it easy to swap between different
database managers, so if you feel in the right mood make a PR to support a new
database and it'll be reviewed ASAP.


# Adding more methods

If you want to add custom methods to the API, we advise to follow the bot's convention:

- Set the SQL query as a global variable whose name starts with `DB_` in `config.py`
- Import it in the `BotBase.database.query` module
- Create a new function that takes the required parameters whose name reflects the query name (without `DB_`)
- Perform the query in a `with` context manager, close the cursor when you're done
- Return `True` or the query result if the query was successful, or an `Exception` subclass if an error occurs
