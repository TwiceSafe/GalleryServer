import time
import uuid
from asyncio import iscoroutinefunction, iscoroutine
from multiprocessing import Queue
from types import coroutine
from typing import Self

from gunicorn.app.wsgiapp import WSGIApplication
from sqlalchemy import TypeDecorator, Integer
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


API_VERSIONS = ["v1.0"]
ERROR_RESPONSE = {
        "error": {
            "code": 1,  # TODO: create own status
            "name": "unknown_api_version",
            "description": "Specified API version is unknown to the server. "
                           "Maybe it is too old or very new, so you should "
                           "either update your application or ask "
                           "administrator to update the server."
        }
    }, 400, {"Content-Type": "application/json"}

async def async_versioned(func, version: str, max_version: str = None, allow_no_version: bool = False, *args, **kwargs):
    result = versioned(func, version, max_version, allow_no_version, *args, **kwargs)
    if iscoroutine(result):
        return await result
    else:
        return result

def versioned(func, version: str = None, max_version: str = None, allow_no_version: bool = False, *args, **kwargs):
    def wrap(versioned_function_string):
        try:
            return getattr(func, versioned_function_string)(*args, **kwargs)
        except TypeError as e:
            message = str(e)
            if "got an unexpected keyword argument" in message:
                unexpected_arg = message.split("'")[1]
                kwargs.pop(unexpected_arg, None)
                return wrap(versioned_function_string)
            else:
                raise

    if version is None:
        if allow_no_version:
            return wrap("nonversioned")
        else:
            return ERROR_RESPONSE

    if version not in API_VERSIONS:
        return ERROR_RESPONSE

    if max_version is not None:
        if API_VERSIONS.index(version) < API_VERSIONS.index(max_version):
            return ERROR_RESPONSE

    api_versions_known_to_client = API_VERSIONS[API_VERSIONS.index(version):]

    for i in api_versions_known_to_client:
        versioned_function_string = f"{i.replace(".", "dot")}"
        try:
            return wrap(versioned_function_string)
        except AttributeError as e:
            if versioned_function_string not in str(e):
                raise

    return ERROR_RESPONSE



