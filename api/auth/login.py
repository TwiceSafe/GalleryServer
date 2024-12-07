import misc
from classes.user import get_user_from_username

MIN_VERSION = 1

def search(*args, **kwargs):

    def v1(username: str, password: str):
        user = get_user_from_username(username)
        if user.password != password:
            raise Exception
        return {
            "code": 200,
            "response": {
                "token": user.generate_token()
            }
        }
    search.v1 = v1

    return misc.versioned(search, min_version=MIN_VERSION, *args, **kwargs)