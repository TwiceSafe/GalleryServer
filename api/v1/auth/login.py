from classes.user import get_user_from_username


def search(username: str, password: str):
    user = get_user_from_username(username)
    if user.password != password:
        raise Exception
    return user.generate_token()