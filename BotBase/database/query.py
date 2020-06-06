import sqlite3.dbapi2 as sqlite3
from ..config import DB_GET_USERS, DB_GET_USER, DB_RELPATH, DB_SET_USER
import logging
import time
from types import FunctionType
import os


def create_database(path: str, query: str):
    if os.path.exists(path):
        logging.warning(f"Database file exists at {path}, running query")
    else:
        logging.warning(f"No database found, creating it at {path}")
    try:
        database = sqlite3.connect(path)
    except sqlite3.Error as connection_error:
        logging.error(f"An error has occurred while connecting to database: {connection_error}")
    else:
        try:
            with database:
                cursor = database.cursor()
                cursor.executescript(query)
                cursor.close()
        except sqlite3.Error as query_error:
            logging.info(f"An error has occurred while executing query: {query_error}")

def get_user(tg_id: int):
    try:
        database = sqlite3.connect(DB_RELPATH)
    except sqlite3.Error as connection_error:
        logging.error(f"An error has occurred while connecting to database: {connection_error}")
    else:
        try:
            with database:
                cursor = database.cursor()
                query = cursor.execute(DB_GET_USER, (tg_id,))
                return query.fetchone()
        except sqlite3.Error as query_error:
            logging.error(f"An error has occurred while executing DB_GET_USER query: {query_error}")
            return query_error

def get_users():
    try:
        database = sqlite3.connect(DB_RELPATH)
    except sqlite3.Error as connection_error:
        logging.error(f"An error has occurred while connecting to database: {connection_error}")
    else:
        try:
            with database:
                cursor = database.cursor()
                query = cursor.execute(DB_GET_USERS)
                return query.fetchall()
        except sqlite3.Error as query_error:
            logging.error(f"An error has occurred while executing DB_GET_USERS query: {query_error}")
            return query_error


def set_user(tg_id: int, uname: str):
    try:
        database = sqlite3.connect(DB_RELPATH)
    except sqlite3.Error as connection_error:
        logging.error(f"An error has occurred while connecting to database: {connection_error}")
    else:
        try:
            with database:
                cursor = database.cursor()
                cursor.execute(DB_SET_USER, (None, tg_id, uname, time.strftime("%d/%m/%Y %T %p")))
                cursor.close()
            return True
        except sqlite3.Error as query_error:
            logging.error(f"An error has occurred while executing DB_GET_USERS query: {query_error}")
            return query_error
