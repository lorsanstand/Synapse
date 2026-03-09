package config

import (
	"log"
	"sync"

	"github.com/ilyakaznacheev/cleanenv"
)

type Config struct {
	ScheduleUrl string `env:"SCHEDULE_URL" env-required:"true"`
}

var (
	instance *Config
	once     sync.Once
)

func GetConfig() *Config {
	once.Do(func() {
		instance = &Config{}

		if err := cleanenv.ReadConfig(".env", instance); err != nil {
			log.Println("File .env not found")

			if err := cleanenv.ReadEnv(instance); err != nil {
				panic("ENV not found")
			}
		}
	})

	return instance
}
