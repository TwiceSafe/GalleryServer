import uuid
from pathlib import Path

import starlette.datastructures

import misc
from classes.user import get_user_from_token_info
from config import get_config


async def post_v1dot0(token_info, file: starlette.datastructures.UploadFile):
    user = get_user_from_token_info(token_info)
    assert isinstance(file, starlette.datastructures.UploadFile)

    file_id = str(uuid.uuid4())

    Path(get_config().data_directory + "/userfiles/v1/" + user.user_id + "/v1").mkdir(parents=True, exist_ok=True)
    with open(get_config().data_directory + "/userfiles/v1/" + user.user_id + "/v1/" + file_id, "wb") as buffer:
        while content := await file.read(1024):
            buffer.write(content)

    return {
        "response": {
            "file_id": file_id
        }
    }, 200

async def post(*args, **kwargs):
    post.v1dot0 = post_v1dot0
    return await misc.async_versioned(post, *args, **kwargs)