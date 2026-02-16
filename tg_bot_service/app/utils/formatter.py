from datetime import date


class ScheduleFormatterMessage:
    @staticmethod
    def format_schedule(data: dict, date_: str):
        if not data:
            return f"{date_}: 🏖 Занятий нет, отдыхай!"

        if date_ == date.today().strftime("%d.%m.%Y"):
            today = "(Сегодня)"
        else:
            today = ""

        text = f"🗓 <b>{data['day_week']} {date_} {today}</b>\n"
        text += "─" * 15 + "\n"

        sorted_pairs = sorted(data['pairs'].items(), key=lambda x: int(x[0]))

        for num, lessons in sorted_pairs:
            for lesson in lessons:

                sub = f" [Гр.{lesson['subgroup']}]" if lesson['subgroup'] else ""
                text += f"<b>{num}️⃣ {lesson['time']}</b>\n"
                text += f"🎓 <b>{lesson['lesson_name']}</b> ({lesson['type']}){sub}\n"
                text += f"👤 {lesson['teacher']}\n"

                audience = lesson['audience'].replace("Учебный корпус", "корп.")
                if "он-лайн" in audience.lower():
                    audience = "🌐 Онлайн"

                text += f"📍 <i>{audience}</i>\n\n"

        return text