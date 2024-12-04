import os

import misc
from classes.user import get_user_from_token_info, user_db_session_maker


async def get(token_info: dict, repository_name: str, commit_id: str):
    worker_pid = os.getpid()
    try:
        return f"{worker_pid}|{misc.data["data"]}"
    except:
        return f"{worker_pid}|Nothing"

async def post(token_info: dict, repository_name: str, commit: dict):
    async with user_db_session_maker() as session:
        user = await get_user_from_token_info(session, token_info)

        misc.data["data"] = commit

        return "добавили"