import uuid

from classes.user import User, UserStatus


def post(username: str, password: str):
    user = User()

    user.user_id = str(uuid.uuid4())
    user.status = UserStatus.ACTIVE
    user.username = username
    user.password = password
    user.save(new=True)

    return user.generate_token()