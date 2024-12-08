from typing import Optional

import misc


def search_v1dot0(error: Optional[int] = None):
    if error:
        return {
            "error": {
                "code": 1,  # TODO: create own status
                "name": "bad_request",
                "description": "You sent bad request on purpose."
            }
        }, 400

    return {
        "response": {
            "hello": "Hi!",
            "api_version": misc.API_VERSIONS[0]
        }
    }, 200

def search_nonversioned(error: Optional[int] = None):
    return search_v1dot0(error)

def search(*args, **kwargs):
    search.v1dot0 = search_v1dot0
    search.nonversioned = search_nonversioned
    return misc.versioned(search, allow_no_version=True, *args, **kwargs)