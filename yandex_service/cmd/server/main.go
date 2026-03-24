package main

import "github.com/lorsanstand/yandex_service/cmd/pkg/config"

func main() {
	cfg, err := config.NewConfig()
	if err != nil {
		return
	}
}
