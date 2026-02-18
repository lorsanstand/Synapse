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


    @staticmethod
    def format_change_notification(data):
        text = f"⚠️ <b>Внимание! Изменение в расписании</b>\n"
        text += f"📅 <b>{data['day']} ({data['day_week']})</b>\n"
        text += "─" * 15 + "\n"

        for i, change in enumerate(data["changes"], 1):
            field_name = change["field"]
            old_val = change["old"] if change["old"] else "—"
            new_val = change["new"] if change["new"] else "❌ Отменено"

            field_map = {
                "lesson_name": "Предмет",
                "teacher": "Преподаватель",
                "audience": "Аудитория",
                "time": "Время",
                "type": "Тип занятия",
                "subgroup": "Подгруппа"
            }
            display_field = field_map.get(field_name, field_name)

            text += f"{i}. <b>{display_field}:</b>\n"
            text += f"   <s>{old_val}</s> ➔ <b>{new_val}</b>\n\n"

        text += "🔔 Проверьте обновленное расписание в меню!"
        return text