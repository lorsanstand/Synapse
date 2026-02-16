from datetime import date, timedelta
import json
from typing import Optional
import logging
import hashlib
import asyncio

from app.utils.parser import Schedule
from app.core.redis import get_redis
from app.core.config import settings
from app.utils.find_changes import FindChanges
from app.schemas.find_changes import Changes
from app.tasks.bot import BotTasks
from app.utils.group import load_groups

log = logging.getLogger(__name__)


class ScheduleService:
    @classmethod
    async def get_schedule(cls, group: int, begin: date, end: date):
        log.debug("Start getting schedule group: %s", group)
        redis = await get_redis()
        dates = []
        schedule: Optional[dict] = {}

        current_date = begin
        while current_date <= end:
            dates.append(current_date.strftime("%d.%m.%Y"))
            current_date += timedelta(days=1)

        schedule_all = await redis.get(str(group))

        if schedule_all is None:
            log.debug("Schedule not found in redis")
            schedule_all = await Schedule.pars_schedule(group, begin, end)
            # await redis.setex(str(group), 61, json.dumps(schedule_all, ensure_ascii=False))

        if isinstance(schedule_all, str):
            schedule_all = json.loads(schedule_all)


        for day in dates:
            schedule[day] = schedule_all.get(day)

        log.info("Successfully get schedule group: %s", group)
        return schedule


    @classmethod
    async def update_schedule(cls, group: int):
        log.debug("Started update schedule group: %s", group)
        redis = await get_redis()
        today = date.today()
        begin_date = today - timedelta(weeks=1)
        end_date = today + timedelta(weeks=2)

        schedule_old = await redis.get(str(group))
        schedule_new = await Schedule.pars_schedule(group, begin_date, end_date)

        if schedule_old is None:
            log.info("Schedule group %s not found in redis", group)
            await redis.setex(str(group), 360, json.dumps(schedule_new, ensure_ascii=False))
            hashes = {}
            for key, value in schedule_new.items():
                encoded_days = json.dumps(value, ensure_ascii=False, sort_keys=True).encode('utf-8')
                day_hash = hashlib.sha256(encoded_days).hexdigest()
                hashes[key] = day_hash

            await redis.hset(f"{group}:hash", mapping=hashes)
            return

        hashes = await redis.hgetall(f"{group}:hash")
        schedule_old = json.loads(schedule_old)

        log.debug("Started search different")
        for key, value in schedule_new.items():
            hash_old = hashes.get(key)
            encoded_value = json.dumps(value, ensure_ascii=False, sort_keys=True).encode('utf-8')
            hash_new = hashlib.sha256(encoded_value).hexdigest()

            if hash_old is None:
                hashes[key] = hash_new
                log.debug("Not found hash maybe new day")

            if hash_old != hash_new:
                hashes[key] = hash_new
                log.info('Found update schedule in %s', key)
                ch = FindChanges.find_changes(old_val=schedule_old[key], new_val=value)
                all_changes = Changes(
                    count=len(ch),
                    day=key,
                    day_week=value["day_week"],
                    changes=ch
                )
                await BotTasks.send_message.kiq(data=all_changes, group=group)
                log.info("Find successfully changed: %s", all_changes)


        hashes = {key: hashes[key] for key in hashes if key in schedule_new}
        await redis.setex(str(group), 360, json.dumps(schedule_new, ensure_ascii=False))
        await redis.hset(f"{group}:hash", mapping=hashes)


    @classmethod
    async def schedule_task_loop(cls):
        while True:
            try:
                groups = await load_groups()
                for group in groups:
                    await cls.update_schedule(group)
                await asyncio.sleep(60)
            except asyncio.CancelledError as ex:
                log.warning("Stopping schedule task")
                break
            except Exception as e:
                log.exception("Error in cycle")
                await asyncio.sleep(5)