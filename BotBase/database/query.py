import sqlite3.dbapi2 as sqlite3
from ..config import DB_GET_USERS, DB_GET_USER, DB_RELPATH, DB_SET_USER, DB_GET_IMEI, DB_SET_IMEI, DB_GET_API_DATE, \
    DB_SET_API_DATE, DB_SET_IMEI_DATA, DB_GET_IMEI_DATA
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


def set_imei(tg_id: int, imei: str):
    try:
        database = sqlite3.connect(DB_RELPATH)
    except sqlite3.Error as connection_error:
        logging.error(f"An error has occurred while connecting to database: {connection_error}")
    else:
        try:
            with database:
                cursor = database.cursor()
                cursor.execute(DB_SET_IMEI, (imei, tg_id))
                cursor.close()
            return True
        except sqlite3.Error as query_error:
            logging.error(f"An error has occurred while executing DB_SET_IMEI query: {query_error}")


def get_imei(tg_id: int):
    try:
        database = sqlite3.connect(DB_RELPATH)
    except sqlite3.Error as connection_error:
        logging.error(f"An error has occurred while connecting to database: {connection_error}")
    else:
        try:
            with database:
                cursor = database.cursor()
                query = cursor.execute(DB_GET_IMEI, (tg_id,))
                return query.fetchone()
        except sqlite3.Error as query_error:
            logging.error(f"An error has occurred while executing DB_GET_IMEI query: {query_error}")


def set_api_date(tg_id: int, timer: FunctionType = time.time):
    try:
        database = sqlite3.connect(DB_RELPATH)
    except sqlite3.Error as connection_error:
        logging.error(f"An error has occurred while connecting to database: {connection_error}")
    else:
        try:
            with database:
                cursor = database.cursor()
                cursor.execute(DB_SET_API_DATE, (int(timer()), tg_id))
                cursor.close()
            return True
        except sqlite3.Error as query_error:
            logging.error(f"An error has occurred while executing DB_SET_API_DATE query: {query_error}")


def get_api_date(tg_id: int):
    try:
        database = sqlite3.connect(DB_RELPATH)
    except sqlite3.Error as connection_error:
        logging.error(f"An error has occurred while connecting to database: {connection_error}")
    else:
        try:
            with database:
                cursor = database.cursor()
                query = cursor.execute(DB_GET_API_DATE, (tg_id,))
                return query.fetchone()
        except sqlite3.Error as query_error:
            logging.error(f"An error has occurred while executing DB_GET_API_DATE query: {query_error}")


def set_imei_data(imei: int, json_data: str):
    try:
        database = sqlite3.connect(DB_RELPATH)
    except sqlite3.Error as connection_error:
        logging.error(f"An error has occurred while connecting to database: {connection_error}")
    else:
        try:
            with database:
                cursor = database.cursor()
                cursor.execute(DB_SET_IMEI_DATA, (imei, json_data))
                cursor.close()
            return True
        except sqlite3.Error as query_error:
            logging.error(f"An error has occurred while executing DB_SET_IMEI_DATA query: {query_error}")


def get_imei_data(imei: int):
    try:
        database = sqlite3.connect(DB_RELPATH)
    except sqlite3.Error as connection_error:
        logging.error(f"An error has occurred while connecting to database: {connection_error}")
    else:
        try:
            with database:
                cursor = database.cursor()
                query = cursor.execute(DB_GET_IMEI_DATA, (imei,))
                return query.fetchone()
        except sqlite3.Error as query_error:
            logging.error(f"An error has occurred while executing DB_GET_IMEI_DATA query: {query_error}")
