import asyncio
import multiprocessing
from pathlib import Path

from connexion import AsyncApp, RestyResolver

import misc
from classes import user
from config import get_config
from misc import StandaloneApplication

config = get_config()

app = AsyncApp(__name__)

app.add_api('api/v1/openapi.yaml', base_path='/api/v1', resolver=RestyResolver("api.v1"))

Path(config.data_directory).mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    asyncio.run(user.create_db_and_tables())

    misc.data = multiprocessing.Manager().dict()

    options = {
        "workers": 4,
        #"workers": (multiprocessing.cpu_count() * 2) + 1,
        "worker_class": "uvicorn.workers.UvicornWorker",
    }
    StandaloneApplication(f"{Path(__file__).stem}:app", options).run()
