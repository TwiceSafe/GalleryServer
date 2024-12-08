import misc
from classes.user import get_user_from_token_info


def search_v1dot0(token_info):
    user = get_user_from_token_info(token_info)
    return {
        "response": {
            "token": user.generate_token(token_info["sub"].split(".")[1])
        }
    }, 200

def search(*args, **kwargs):
    search.v1dot0 = search_v1dot0
    return misc.versioned(search, *args, **kwargs)