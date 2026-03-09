package schedule

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strconv"
	"time"

	"github.com/lorsanstand/homework_service/app/internal/config"
)

type Pair struct {
	Time       string `json:"time"`
	Type       string `json:"type"`
	LessonName string `json:"lesson_name"`
	Audience   string `json:"audience"`
	Subgroup   *int   `json:"subgroup"`
}

type Day struct {
	DayWeek string            `json:"day_week"`
	Pairs   map[string][]Pair `json:"pairs"`
}

func GetSchedule(group int, begin time.Time, end time.Time) (map[string]Day, error) {
	cfg := config.GetConfig()
	beginStr := begin.Format("2006-01-02")
	endStr := end.Format("2006-01-02")

	base, err := url.Parse(cfg.ScheduleUrl)
	if err != nil {
		return nil, fmt.Errorf("error parse url: %v", err)
	}

	params := url.Values{}
	params.Add("group", strconv.Itoa(group))
	params.Add("begin", beginStr)
	params.Add("end", endStr)

	base.RawQuery = params.Encode()

	resp, err := http.Get(base.String())
	if err != nil {
		return nil, fmt.Errorf("error answer server")
	}

	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("server returned non-200 status: %d", resp.StatusCode)
	}

	schedule := make(map[string]Day)

	if err := json.NewDecoder(resp.Body).Decode(&schedule); err != nil {
		return nil, fmt.Errorf("failed to decode schedule: %w", err)
	}

	return schedule, nil
}
