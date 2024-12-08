import json
from pathlib import Path

import misc
from classes.user import get_user_from_token_info
from config import get_config


def get(*args, **kwargs):
    def v1dot0(token_info: dict, repository_name: str, commit_id: str):
        user = get_user_from_token_info(token_info)
        Path(get_config().data_directory + "/usercommits/v1/" + user.user_id + "/v1/" + repository_name).mkdir(
            parents=True, exist_ok=True)
        if not Path(
                get_config().data_directory + "/usercommits/v1/" + user.user_id + "/v1/" + repository_name + "/" + commit_id).is_file():
            return {
                "error": {
                    "code": 1,  # TODO: create own status
                    "name": "not_found",
                    "description": "No commit with this id was found."
                }
            }, 400
        return {
            "response": {
                "commit": json.loads(open(
                    get_config().data_directory + "/usercommits/v1/" + user.user_id + "/v1/" + repository_name + "/" + commit_id,
                    "r").read())
            }
        }, 200

    get.v1dot0 = v1dot0

    return misc.versioned(get, *args, **kwargs)


def post(*args, **kwargs):
    def v1dot0(token_info: dict, repository_name: str, commit: dict):
        user = get_user_from_token_info(token_info)
        commit_id = misc.handle_incoming_commit(user, repository_name, commit)
        return {
            "response": {
                "commit_id": commit_id
            }
        }, 200

    post.v1dot0 = v1dot0

    return misc.versioned(post, *args, **kwargs)
