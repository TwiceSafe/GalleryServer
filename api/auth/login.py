import misc
from classes.user import get_user_from_username

def search(*args, **kwargs):

    def v1dot0(username: str, password: str):
        user = get_user_from_username(username)
        if user.password != password:
            raise Exception
        return {
            "response": {
                "token": user.generate_token()
            }
        }, 200
    search.v1dot0 = v1dot0

    return misc.versioned(search, *args, **kwargs)