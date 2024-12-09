import json
import uuid
from pathlib import Path

import misc
from classes.user import get_user_from_token_info
from config import get_config

spec_paths = {
    "v1.0": {
        "/chain/{chain_name}/event": {
            "post": {
                "summary": "Add new event",
                "security": [
                    {
                        "jwt": ["secret"]
                    }
                ],
                "parameters": [
                    {
                        "name": "chain_name",
                        "description": "Chain name",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "requestBody": {
                    "x-body-name": "event",
                    "description": "Event",
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
                        "description": "Added new event",
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
        "/chain/{chain_name}/event/{event_id}": {
            "get": {
                "summary": "Get event data",
                "security": [
                    {
                        "jwt": ["secret"]
                    }
                ],
                "parameters": [
                    {
                        "name": "chain_name",
                        "description": "Chain name",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "event_id",
                        "description": "Event ID",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Event info",
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


def get_v1dot0(token_info: dict, chain_name: str, event_id: str):
    user = get_user_from_token_info(token_info)
    Path(get_config().data_directory + "/userevents/v1/" + user.user_id + "/v1/" + chain_name).mkdir(
        parents=True, exist_ok=True)
    if not Path(
            get_config().data_directory + "/userevents/v1/" + user.user_id + "/v1/" + chain_name + "/" + event_id).is_file():
        return {
            "error": {
                "code": 1,  # TODO: create own status
                "name": "not_found",
                "description": "No event with this id was found."
            }
        }, 400
    return {
        "response": {
            "event": json.loads(open(
                get_config().data_directory + "/userevents/v1/" + user.user_id + "/v1/" + chain_name + "/" + event_id,
                "r").read())
        }
    }, 200


def post_v1dot0(token_info: dict, chain_name: str, event: dict):
    user = get_user_from_token_info(token_info)
    temp_id = str(uuid.uuid4())
    misc.add_event_requests_queue.put(misc.AddEventRequest(temp_id, user.user_id, chain_name, event))
    while True:
        try:
            response: misc.AddEventResponse = misc.add_event_responses_queue.get()

            if response.temp_id != temp_id:
                misc.add_event_responses_queue.put(response)
                continue

            return response.response
        except:
            return None
