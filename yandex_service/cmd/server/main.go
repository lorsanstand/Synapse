package main

import (
	"log/slog"
	"net/http"
	//"github.com/lorsanstand/yandex_service/pkg/config"

	"github.com/lorsanstand/yandex_service/internal/integration/schedule"
	"github.com/lorsanstand/yandex_service/internal/yandex"
	"github.com/lorsanstand/yandex_service/pkg/config"
)

func main() {
	cfg, err := config.NewConfig()
	if err != nil {
		return
	}

	sch, _ := schedule.NewScheduleService(cfg.ScheduleURL)

	yan := yandex.NewYandex(sch)

	mux := http.NewServeMux()

	mux.HandleFunc("POST /", yan.Response)
	err = http.ListenAndServe("0.0.0.0:9000", mux)
	if err != nil {
		slog.Error("Server crashed", "error", err)
	}
}
