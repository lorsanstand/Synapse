from typing import List
import time
import logging
import json

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)

async def load_groups() -> List[int]:
    start_time = time.perf_counter()
    async with httpx.AsyncClient() as client:

        try:
            response = await client.get(settings.TG_BACKEND_BOT_URL)
        except httpx.ConnectError as e:
            log.error("Groups getting error %s", e)
            return []

        if response.status_code != 200:
            log.error("Groups getting error status code: %s", response.status_code)
            return []

    process_time = time.perf_counter() - start_time
    log.debug("Groups completed successfully time: %.3fs", process_time)

    return json.loads(response.content)