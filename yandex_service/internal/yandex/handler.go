package yandex

import (
	"encoding/json"
	"log/slog"
	"net/http"
	"time"

	"github.com/lorsanstand/yandex_service/internal/integration/schedule"
	"github.com/lorsanstand/yandex_service/pkg/respond"
)

type IntegrationSchedule interface {
	GetSchedule(group int, begin time.Time, end time.Time) (map[string]schedule.Day, error)
}

type Yandex struct {
	schedule IntegrationSchedule
	respond  respond.Respond
}

func NewYandex(integrationSchedule IntegrationSchedule) *Yandex {
	return &Yandex{schedule: integrationSchedule}
}

func (y *Yandex) Response(w http.ResponseWriter, r *http.Request) {
	var req YandexRequest

	defer r.Body.Close()

	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		slog.Error("error JSON decode", "error", err)
		return
	}

	y.scheduleAnswer(w, req)
}
