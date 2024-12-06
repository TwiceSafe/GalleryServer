import logging
import multiprocessing
import sqlite3
import threading
import time
import uuid
from multiprocessing import Queue
from sqlite3 import Connection
from typing import Self

from gunicorn.app.wsgiapp import WSGIApplication
from sqlalchemy import TypeDecorator, Integer
from sqlalchemy.dialects.sqlite.base import SQLiteDialect
from sqlalchemy.orm import declarative_base, DeclarativeBase


def current_timestamp() -> int:
    return int(time.time())


Base: DeclarativeBase = declarative_base()


class IntEnum(TypeDecorator):
    """
    Enables passing in a Python enum and storing the enum's *value* in the db.
    The default would have stored the enum's *name* (ie the string).

    https://gist.github.com/hasansezertasan/691a7ef67cc79ea669ff76d168503235
    """

    impl = Integer

    def __init__(self, enumtype, *args, **kwargs):
        super(IntEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value: Self, dialect):
        if isinstance(value, int):
            return value

        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)

class StandaloneApplication(WSGIApplication):
    def __init__(self, app_uri, options=None):
        self.options = options or {}
        self.app_uri = app_uri
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.app_uri


commit_requests_queue: Queue
commit_responses_queue: Queue


class CommitRequest:
    def __init__(self, temp_id: str, user_id: str, repository_name: str, commit: dict):
        self.temp_id = temp_id
        self.user_id = user_id
        self.repository_name = repository_name
        self.commit = commit

class CommitResponse:
    def __init__(self, temp_id: str, result: int, commit_id: str):
        self.temp_id = temp_id
        self.result = result
        self.commit_id = commit_id


def handle_incoming_commit(user, repository_name, commit):
    temp_id = str(uuid.uuid4())
    commit_requests_queue.put(CommitRequest(temp_id, user.user_id, repository_name, commit))
    while True:
        try:
            response: CommitResponse = commit_responses_queue.get()

            if response.temp_id != temp_id:
                commit_responses_queue.put(response)
                continue

            return response.commit_id
        except:
            return None

#class MPSQLiteCursorWrapper:
#    def __init__(self, connection, *args, **kwargs):
#        self.connection = connection
#        self.args = args
#        self.kwargs = kwargs
#        self.cursor = self.connection.cursor(*args, **kwargs)
#
#    def __getattr__(self, name):
#        print("(Cursor) Starting getting attribute",name)
#        resp = getattr(self.cursor, name)
#        print("(Cursor) Getting attribute", name, "and response is", resp)
#        return resp

class MPSQLiteConnectionRequest:
    def __init__(self, request_id, name, args, kwargs):
        self.request_id = request_id
        self.name = name
        self.args = args
        self.kwargs = kwargs

class MPSQLiteConnectionResponse:
    def __init__(self, request_id, result):
        self.request_id = request_id
        self.result = result

class MPSQLiteProxiedAttributes:
    def __init__(self, name, request_queue, response_queue):
        self.__name = name
        self.__request_queue: Queue = request_queue
        self.__response_queue: Queue = response_queue

    def __call__(self, *args, **kwargs):
        request_id = str(uuid.uuid4())
        self.__request_queue.put(MPSQLiteConnectionRequest(request_id, self.__name, args, kwargs))
        # commit_requests_queue.put(CommitRequest(temp_id, user.user_id, repository_name, commit))
        while True:
            try:
                response: MPSQLiteConnectionResponse = self.__response_queue.get()

                if response.request_id != request_id:
                    self.__response_queue.put(response)
                    continue


                return response.result
            except:
                return None

class MPSQLiteConnectionWrapper:
    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs

        self.__request_queue: Queue = multiprocessing.Manager().Queue()
        self.__response_queue: Queue = multiprocessing.Manager().Queue()

        t = threading.Thread(target=self.__connection_thread)
        t.daemon = True
        t.start()
        self.__thread = t

    def __connection_thread(self):
        connection: Connection = sqlite3.connect(*self.__args, **self.__kwargs)
        while True:
            try:
                request: MPSQLiteConnectionRequest = self.__request_queue.get()
                result = getattr(connection, request.name)(*request.args, **request.kwargs)
                # Код ниже не работает
                self.__response_queue.put(MPSQLiteConnectionResponse(request.request_id, result), block=False)
                # Код выше не работает
            except:
                continue

    #def cursor(self, *args, **kwargs):
    #    print("Custom cursor called")
    #    print(args, kwargs)
    #
    #    temp_id = str(uuid.uuid4())
    #    commit_requests_queue.put(CommitRequest(temp_id, user.user_id, repository_name, commit))
    #    while True:
    #        try:
    #            response: CommitResponse = commit_responses_queue.get()
    #
    #            if response.temp_id != temp_id:
    #                commit_responses_queue.put(response)
    #                continue
    #
    #            return response.commit_id
    #        except:
    #            return None
    #    #return MPSQLiteCursorWrapper(self.connection, *args, **kwargs)
    #    #return self._connection.cursor(*args, **kwargs)

    def __getattr__(self, name):
        print("(Connection) Starting getting attribute",name)
        #resp = getattr(self.connection, name)
        resp = MPSQLiteProxiedAttributes(name, self.__request_queue, self.__response_queue)
        print("(Connection) Getting attribute", name, "and response is", resp)
        return resp


connections: dict[str, MPSQLiteConnectionWrapper] = {}


class MPSQLiteWrapper:
    # noinspection PyMethodMayBeStatic
    def connect(self, *args, **kwargs):
        if kwargs["database"] not in connections:
            connections[kwargs["database"]] = MPSQLiteConnectionWrapper(*args, **kwargs)
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
