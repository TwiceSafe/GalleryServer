import uuid

from classes.user import User, UserStatus, get_user_from_username


def post(username: str, password: str):
    user = get_user_from_username(username, raise_error=False)
    if user is not None:
        return None, 403
    user = User()

    user.user_id = str(uuid.uuid4())
    user.status = UserStatus.ACTIVE
    user.username = username
    user.password = password
    user.save(new=True)

    return user.generate_token()