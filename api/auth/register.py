import uuid

import misc
from classes.user import User, UserStatus, get_user_from_username


def post_v1dot0(username: str, password: str):
    user = get_user_from_username(username, raise_error=False)
    if user is not None:
        return {
            "error": {
                "code": 1,  # TODO: create own status
                "name": "user_already_exists",
                "description": "User with specified username is already present in our database. Can't register with this username."
            }
        }, 400
    user = User()

    user.user_id = str(uuid.uuid4())
    user.status = UserStatus.ACTIVE
    user.username = username
    user.password = password
    user.save(new=True)

    return {
        "response": {
            "token": user.generate_token()
        }
    }, 200

def post(*args, **kwargs):
    post.v1dot0 = post_v1dot0
    return misc.versioned(post, *args, **kwargs)