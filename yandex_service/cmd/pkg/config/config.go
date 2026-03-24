package config

import (
	"fmt"
	"log/slog"

	"github.com/ilyakaznacheev/cleanenv"
)

type config struct {
	ScheduleURL string `env:"SCHEDULE_URL" env-required:"true"`
}

func NewConfig() (*config, error) {
	var cfg config

	if err := cleanenv.ReadConfig(".env", &cfg); err != nil {
		slog.Warn("Failed read config in file", "error", err)

		if err := cleanenv.ReadEnv(&cfg); err != nil {
			slog.Error("ENV not found", "error", err)
			return nil, fmt.Errorf("ENV not found")
		}
	}

	return &cfg, nil
}
