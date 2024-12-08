import misc
from classes.user import get_user_from_token_info


def search_v1dot0(token_info: dict, repository_name: str):
    user = get_user_from_token_info(token_info)
    head = user.get_head(repository_name)
    if head is None:
        return {
            "error": {
                "code": 1,  # TODO: create own status
                "name": "not_found",
                "description": "This repository has not been initiated yet because of no HEAD file."
            }
        }, 400
    return {
        "response": {
            "head": head
        }
    }

def search(*args, **kwargs):
    search.v1dot0 = search_v1dot0
    return misc.versioned(search, *args, **kwargs)

# no post/put as there will be no force push