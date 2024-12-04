import os
import uuid
from asyncio import QueueEmpty
from pathlib import Path

import misc
from classes.user import get_user_from_token_info, user_db_session_maker
from config import get_config

async def get(token_info: dict, repository_name: str, commit_id: str):
    async with user_db_session_maker() as session:
        user = await get_user_from_token_info(session, token_info)
        Path(get_config().data_directory + "/usercommits/v1/" + user.user_id + "/v1/" + repository_name).mkdir(
            parents=True, exist_ok=True)
        if not Path(
                get_config().data_directory + "/usercommits/v1/" + user.user_id + "/v1/" + repository_name + "/"+commit_id).is_file():
            return None, 404
        return open(get_config().data_directory + "/usercommits/v1/" + user.user_id + "/v1/" + repository_name + "/" + commit_id,
                    "r").read()


async def post(token_info: dict, repository_name: str, commit: dict):
    async with user_db_session_maker() as session:
        user = await get_user_from_token_info(session, token_info)

        temp_id = str(uuid.uuid4())
        misc.append_commit_requests.put(misc.CommitAppendRequest(temp_id, user.user_id, repository_name, commit))
        while True:
            try:
                queue_item: misc.CommitAppendResponse = misc.append_commit_responses.get()

                if queue_item.temp_id != temp_id:
                    misc.append_commit_responses.put(queue_item)
                    continue

                return queue_item.commit_id
            except:
                return "error", 500