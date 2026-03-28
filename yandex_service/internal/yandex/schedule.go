package yandex

import (
	"fmt"
	"log/slog"
	"net/http"
	"time"

	"github.com/lorsanstand/yandex_service/pkg/utils/week"
)

func (y *Yandex) scheduleAnswer(w http.ResponseWriter, req YandexRequest) {
	day, err := y.getDate(req)
	if err != nil {
		y.respond.RespondJSON(w, 200, failedYandexResponse())
		return
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

func (y *Yandex) getDate(req YandexRequest) (time.Time, error) {
	day := time.Now()

	ScheduleDay := req.Request.NLU.Intents.Schedule.Slots.When.Value
	DayOfWeek := req.Request.NLU.Intents.Schedule.Slots.DayOfWeek.Value

	if ScheduleDay.DayIsRelative {
		day = day.AddDate(0, 0, ScheduleDay.Day)

	} else if DayOfWeek != "" {
		NumDay, ok := week.SearchDay(DayOfWeek)
		if !ok {
			return time.Time{}, fmt.Errorf("failed search day")
		}

		num := NumDay - int(day.Weekday())
		if num < 0 {
			day = day.AddDate(0, 0, 7)
		}

		day = day.AddDate(0, 0, num)
	} else {
		return time.Time{}, fmt.Errorf("failed search day")
	}

	return day, nil
}
