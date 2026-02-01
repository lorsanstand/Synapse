import logging
from datetime import date
import uvicorn
import uuid
import time
from contextlib import asynccontextmanager
import asyncio
from typing import Dict, Optional

from fastapi import FastAPI, Request, Response

from app.services.schedule import ScheduleService
from app.core.log_config import set_logging
from app.core.config import settings
from app.core.redis import init_redis, close_redis
from app.schemas.schedule import Day

set_logging()
log = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    log.info("Redis connected")
    task = asyncio.create_task(ScheduleService.schedule_task_loop())
    yield
    await close_redis()
    log.info("Redis disconnected")
    task.cancel()

app = FastAPI(
    lifespan=lifespan
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.perf_counter()

    log.info(
        "Started method=%s path=%s",
        request.method, request.url.path,
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "type": "start"
        }
    )
    try:
        response: Response = await call_next(request)
        process_time = time.perf_counter() - start_time

        log.info(
            "Finished method=%s path=%s status=%s duration=%.3fs",
            request.method, request.url.path, response.status_code, process_time,
            extra={
                "request_id": request_id,
                "status": response.status_code,
                "duration": process_time,
                "type": "end"
            }
        )
        return response

    except Exception as e:
        log.error("Request failed id=%s error=%s", request_id, str(e))
        raise


@app.get("/schedule")
async def get_schedule(group: int, begin: date, end: date) -> Dict[str, Optional[Day]]:
    return await ScheduleService.get_schedule(group, begin, end)

@app.post("/test")
async def test(group: int):
    return await ScheduleService.update_schedule(group)


if __name__ == "__main__":
    if settings.MODE == "PROD":
        UVICORN_PARAMS = dict(
            host=settings.HOST,
            port=settings.PORT,
            reload=False,
            workers=settings.WORKERS,
            access_log=False
        )
    else:
        UVICORN_PARAMS = dict(
            host=settings.HOST,
            port=settings.PORT,
            reload=True,
            access_log=False
        )
    uvicorn.run("app.main:app", **UVICORN_PARAMS)