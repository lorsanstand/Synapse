package yandex

import (
	"log/slog"
	"net/http"
	"time"
)

func (y *Yandex) scheduleAnswer(w http.ResponseWriter, req YandexRequest) {
	day := y.getDate(req)

	Schedule, err := y.schedule.GetSchedule(90002595, day, day)
	if err != nil {
		slog.Warn("Failed get schedule", "error", err)
		y.respond.RespondJSON(w, 200, failedYandexResponse())
		return
	}
	scheduleDay := Schedule[day.Format("02.01.2006")]
	response := scheduleYandexResponse(scheduleDay)

	y.respond.RespondJSON(w, 200, response)
}

var weekDay = map[string]int{"воскресенье": 0, "понедельник": 1, "вторник": 2, "среда": 3, "четверг": 4, "пятница": 5, "суббота": 6}

func (y *Yandex) getDate(req YandexRequest) time.Time {
	now := time.Now()
	day := now

	ScheduleDay := req.Request.NLU.Intents.Schedule.Slots.When.Value
	DayOfWeek := req.Request.NLU.Intents.Schedule.Slots.DayOfWeek.Value

	if ScheduleDay.DayIsRelative {
		day = day.AddDate(0, 0, ScheduleDay.Day)
	} else if DayOfWeek != "" {
		num := weekDay[DayOfWeek] - int(day.Weekday())
		day = day.AddDate(0, 0, num)
	}

	return day
}
