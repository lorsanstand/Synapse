package week

import "strings"

var weekDay = map[string]int{"воскресен": 0, "понедельник": 1, "вторник": 2, "сред": 3, "четверг": 4, "пятниц": 5, "суббот": 6}

func SearchDay(WeekDay string) (int, bool) {
	WeekDay = strings.ToLower(WeekDay)
	for day, num := range weekDay {
		if !strings.Contains(WeekDay, day) {
			continue
		}

		return num, true
	}
	return 0, false
}
