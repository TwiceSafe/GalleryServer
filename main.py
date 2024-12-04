import asyncio
import multiprocessing
import threading
from pathlib import Path

from connexion import AsyncApp, RestyResolver

import misc
from classes import user
from classes.user import user_db_session_maker, get_user_from_user_id
from config import get_config
from misc import StandaloneApplication

config = get_config()

app = AsyncApp(__name__)

app.add_api('api/v1/openapi.yaml', base_path='/api/v1', resolver=RestyResolver("api.v1"))

Path(config.data_directory).mkdir(parents=True, exist_ok=True)

def __worker_thread():
    async def async_thread():
        async with user_db_session_maker() as session:
            while True:
                try:
                    request: misc.CommitAppendRequest = misc.append_commit_requests.get()
                    user = await get_user_from_user_id(session, request.user_id)
                    commit_id = user.add_commit(request.repository_name, request.commit)
                    queue_item_result = misc.CommitAppendResponse(request.temp_id, commit_id)
                    misc.append_commit_responses.put(queue_item_result)
                except:
                    continue

    asyncio.run(async_thread())


if __name__ == "__main__":
    asyncio.run(user.create_db_and_tables())

    misc.append_commit_requests = multiprocessing.Manager().Queue()
    misc.append_commit_responses = multiprocessing.Manager().Queue()

    t = threading.Thread(target=__worker_thread)
    t.daemon = True
    t.start()

    options = {
        "workers": (multiprocessing.cpu_count() * 2) + 1,
        "worker_class": "uvicorn.workers.UvicornWorker",
    }
    StandaloneApplication(f"{Path(__file__).stem}:app", options).run()
