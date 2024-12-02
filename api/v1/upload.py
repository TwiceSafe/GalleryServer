import uuid
from pathlib import Path

import starlette.datastructures

from classes.user import get_user_from_token_info, user_db_session_maker
from config import get_config


async def post(token_info, file: starlette.datastructures.UploadFile):
    async with user_db_session_maker() as session:
        user = await get_user_from_token_info(session, token_info)
        assert isinstance(file, starlette.datastructures.UploadFile)

        file_id = str(uuid.uuid4())

        Path(get_config().data_directory+"/userfiles/v1/"+user.user_id+"/v1").mkdir(parents=True, exist_ok=True)
        with open(get_config().data_directory+"/userfiles/v1/"+user.user_id+"/v1/"+file_id, "wb") as buffer:
            while content := await file.read(1024):
                buffer.write(content)

        return f"Hello", 200