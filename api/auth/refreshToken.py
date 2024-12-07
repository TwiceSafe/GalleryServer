from classes.user import get_user_from_token_info


def search(token_info, v: int):
    user = get_user_from_token_info(token_info)
    return user.generate_token(token_info["sub"].split(".")[1])