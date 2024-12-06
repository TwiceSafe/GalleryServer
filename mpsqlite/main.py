import logging

from sqlalchemy.dialects.sqlite.base import SQLiteDialect

from mpsqlite.connection import MPSQLiteConnectionWrapper

connections: dict[str, MPSQLiteConnectionWrapper] = {}


class MPSQLiteWrapper:
    # noinspection PyMethodMayBeStatic
    def connect(self, *args, **kwargs):
        if kwargs["database"] not in connections:
            connections[kwargs["database"]] = MPSQLiteConnectionWrapper(args, kwargs)
        return connections[kwargs["database"]]

    def __getattr__(self, name):
        logging.debug("(SQLite) Starting getting attribute ", name)
        import sqlite3
        resp = getattr(sqlite3, name)
        logging.debug("(SQLite) Getting attribute ", name, " and response is ", resp)
        return resp


mpsqlite = MPSQLiteWrapper()


class MPSQLiteDialect(SQLiteDialect):
    name = "mpsqlite"
    driver = "sqlite3"

    supports_statement_cache = True

    @classmethod
    def import_dbapi(cls):
        return mpsqlite