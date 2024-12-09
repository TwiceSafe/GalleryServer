import json
import uuid
from pathlib import Path

import misc
from classes.user import get_user_from_token_info
from config import get_config

spec_paths = {
    "v1.0": {
        "/repository/{repository_name}/commit": {
            "post": {
                "summary": "Get new JWT token for this device",
                "security": [
                    {
                        "jwt": ["secret"]
                    }
                ],
                "parameters": [
                    {
                        "name": "repository_name",
                        "description": "Repository name",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "requestBody": {
                    "x-body-name": "commit",
                    "description": "Commit data",
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Add new commit",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    }
                }
            }
        },
        "/repository/{repository_name}/commit/{commit_id}": {
            "get": {
                "summary": "Get new JWT token for this device",
                "security": [
                    {
                        "jwt": ["secret"]
                    }
                ],
                "parameters": [
                    {
                        "name": "repository_name",
                        "description": "Repository name",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "commit_id",
                        "description": "Commit ID",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Commit info",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad request",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


def get_v1dot0(token_info: dict, repository_name: str, commit_id: str):
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


def post_v1dot0(token_info: dict, repository_name: str, commit: dict):
    user = get_user_from_token_info(token_info)
    temp_id = str(uuid.uuid4())
    misc.commit_requests_queue.put(misc.CommitRequest(temp_id, user.user_id, repository_name, commit))
    while True:
        try:
            response: misc.CommitResponse = misc.commit_responses_queue.get()

            if response.temp_id != temp_id:
                misc.commit_responses_queue.put(response)
                continue

            return response.response
        except:
            return None
