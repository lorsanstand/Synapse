package yandex

import (
	"log/slog"
	"net/http"
	"time"
)

func (y *Yandex) scheduleAnswer(w http.ResponseWriter, req YandexRequest) {
	now := time.Now()
	day := now
	ScheduleDay := req.Request.NLU.Intents.Schedule.Slots.When.Value

	if !ScheduleDay.DayIsRelative {
		day = time.Date(
			now.Year(),
			time.Month(ScheduleDay.Month),
			ScheduleDay.Day,
			0,
			0,
			0,
			0,
			time.UTC,
		)
	} else {
		day = time.Date(
			now.Year(),
			now.Month(),
			now.Day()+ScheduleDay.Day,
			0,
			0,
			0,
			0,
			time.UTC,
		)
	}

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
