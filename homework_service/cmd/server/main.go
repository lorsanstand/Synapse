package main

import (
	"fmt"
	"log"
	"time"

	"github.com/lorsanstand/homework_service/app/internal/schedule"
)

func main() {
	begin := time.Date(2026, time.February, 24, 0, 0, 0, 0, time.UTC)
	end := time.Date(2026, time.February, 27, 0, 0, 0, 0, time.UTC)
	sch, err := schedule.GetSchedule(90002595, begin, end)
	if err != nil {
		log.Println(err)
	}
	for _, value := range sch {
		fmt.Println(value.Pairs)
	}
}
