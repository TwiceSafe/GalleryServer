import asyncio
from pathlib import Path

import uvicorn
from connexion import AsyncApp, RestyResolver

from classes import user
from config import get_config

config = get_config()

app = AsyncApp(__name__)

app.add_api('api/v1/openapi.yaml', base_path='/api/v1', resolver=RestyResolver("api.v1"))

Path(config.data_directory).mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    asyncio.run(user.create_db_and_tables())
    uvicorn.run("main:app", reload=True)
