from typing import Optional


def search(error: Optional[int] = None, v: Optional[int] = None):
    if error:
        return {
            "status": 400,
            "error": {
                "name": "badrequest",
                "description": "You sent bad request on purpose."
            }
        }, 400

    return {
        "status": 200,
        "response": {
            "hello": "Hi!",
            "api_version": 1
        }
    }