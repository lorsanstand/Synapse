import logging
from datetime import date
import re

from bs4 import BeautifulSoup
import httpx
from fastapi import HTTPException, status

from app.core.config import settings

log = logging.getLogger(__name__)


class Schedule:
    @classmethod
    async def pars_schedule(cls, group: int, begin: date, end: date):
        log.debug("Start parsing schedule group: %s", group)

        try:
            week = begin.strftime("%d%m%Y") + end.strftime("%d%m%Y")
            src = await cls.scrap_schedule(group, week, settings.SCRAP_URL)
        except Exception as ex:
            log.warning("Failed scrapping")
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail="Failed scrapping")

        parse_schedule: dict = {}
        soup = BeautifulSoup(src, "lxml")

        if "Нет занятий" in soup.find("b").get_text(strip=True):
            return {}

        table = soup.find("table", {"id": "shedule"})

        for tr in table.find_all("tr"):
            # 1. Обработка заголовка дня (оставляем как было)
            if tr.find("td", class_="colspan"):
                data = tr.find("span", class_="h3").get_text(strip=True)
                date_ = data.split(" ")
                date_schedule = date_[0]
                day = date_[1]
                parse_schedule[date_schedule] = {"day_week": day, "pairs": {}}
                continue

            lessons = tr.find_all("td", {"id": "lesson"})
            if not lessons:  # Пропускаем пустые строки, если есть
                continue

            # 2. Обработка номера пары и времени
            # Если в строке rowspan, то td_num будет только в первой строке группы
            td_num = tr.find("td", {"id": "num"})
            if td_num is not None:
                pair = td_num.find("span").get_text(strip=True)
                time = tr.find("td", {"id": "time"}).get_text(strip=True)
                parse_schedule[date_schedule]["pairs"][pair] = []

            # 3. Извлечение данных (исправлено под новую верстку)

            # Тип занятия (лек, пр.з., ком.)
            type_lesson = lessons[0].get_text(strip=True)

            # Предмет: если нет ссылки <a>, берем просто текст из ячейки
            lesson_anchor = lessons[1].find("a")
            if lesson_anchor:
                lesson = lesson_anchor.get_text(strip=True)
            else:
                # Для Географии и подобных: берем весь текст и чистим от лишних пробелов
                lesson = lessons[1].get_text(strip=True)

            # Преподаватель: аналогично, если нет <a>, берем текст
            teacher_td = tr.find("td", {"id": "teacher"})
            if teacher_td:
                teacher_anchor = teacher_td.find("a")
                teacher = teacher_anchor.get_text(strip=True) if teacher_anchor else teacher_td.get_text(
                    strip=True).replace("преп.", "").strip()
            else:
                teacher = ""

            # Аудитория
            aud_td = tr.find("td", {"id": "aud"})
            audience = aud_td.get_text(" ", strip=True).replace("ауд.", "").strip() if aud_td else ""

            # Подгруппа (твой регулярный поиск по тексту ячейки)
            match = re.search(r'п/г.*?(\d+)\s+подгруппа', lessons[1].get_text(strip=True))
            subgroup = int(match.group(1)) if match else None

            # Сохраняем строго в твоем формате
            parse_schedule[date_schedule]["pairs"][pair].append(
                {
                    "time": time,
                    "type": type_lesson,
                    "lesson_name": lesson,
                    "teacher": teacher,
                    "audience": audience,
                    "subgroup": subgroup
                }
            )

        return parse_schedule

        # for tr in table.find_all("tr"):
        #     if tr.find("td", class_="colspan"):
        #         data = tr.find("span", class_="h3").get_text(strip=True)
        #         date_ = data.split(" ")
        #         date_schedule = date_[0]
        #         day = date_[1]
        #         parse_schedule[date_schedule] = {"day_week": day, "pairs": {}}
        #         continue
        #
        #     lessons = tr.find_all("td", {"id": "lesson"})
        #
        #     if tr.find("td", {"id": "num"}) is not None:
        #         pair = tr.find("td", {"id": "num"}).find("span").get_text(strip=True)
        #         time = tr.find("td", {"id": "time"}).get_text(strip=True)
        #         parse_schedule[date_schedule]["pairs"][pair] = []
        #
        #     type_lesson = lessons[0].find("small").get_text(strip=True)
        #     if lessons[1].find("a") is None:
        #         continue
        #     lesson = lessons[1].find("a").get_text(strip=True)
        #     teacher = tr.find("td", {"id": "teacher"}).find("a").get_text(strip=True)
        #     audience = tr.find("td", {"id": "aud"}).get_text(strip=True)
        #
        #     match = re.search(r'п/г.*?(\d+)\s+подгруппа', lessons[1].get_text(strip=True))
        #     if match:
        #         subgroup = int(match.group(1))
        #     else:
        #         subgroup = None
        #
        #     parse_schedule[date_schedule]["pairs"][pair].append(
        #         {
        #             "time": time,
        #             "type": type_lesson,
        #             "lesson_name": lesson,
        #             "teacher": teacher,
        #             "audience": audience,
        #             "subgroup": subgroup
        #         }
        #     )
        # log.info("Successfully parsing")
        #
        # return parse_schedule


    @classmethod
    async def scrap_schedule(cls, group: int, week: str, url: str):
        async with httpx.AsyncClient() as client:
            log.debug("Start scrapping")
            data = dict(
                group=group,
                week=week
            )

            response = await client.post(url, data=data)
            response.raise_for_status()

            log.info("Successfully scrapping")
            return response.content