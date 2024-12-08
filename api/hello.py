from typing import Optional

import misc


def search(*args, **kwargs):
    def v1dot0(error: Optional[int] = None):
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
    search.v1dot0 = v1dot0

    def nonversioned(error: Optional[int] = None):
        return v1dot0(error)
    search.nonversioned = nonversioned

    return misc.versioned(search, allow_no_version=True, *args, **kwargs)