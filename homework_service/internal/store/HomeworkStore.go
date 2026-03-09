package store

import (
	"sync"
	"time"
)

type Homework struct {
	Id          int       `json:"id"`
	Subject     string    `json:"subject"`
	UserId      int       `json:"user_id"`
	ScheduledAt time.Time `json:"scheduled_at"`
	Content     string    `json:"content"`
}

type HomeworkStore struct {
	sync.RWMutex

	homeworks map[int]Homework
}
