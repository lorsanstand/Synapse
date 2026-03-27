package yandex

type YandexRequest struct {
	Request request `json:"request"`
	Session session `json:"session"`
	State   state   `json:"state"`
}

type session struct {
	AwaitingGroup bool `json:"awaiting_group"`
}

type user struct {
	Group int `json:"group"`
}

type state struct {
	User    user    `json:"user"`
	Session session `json:"session"`
}

type entity struct {
	Type  string `json:"type"`
	Value any    `json:"value"`
}

type yandexDatetime struct {
	Month         int  `json:"month"`
	Day           int  `json:"day"`
	DayIsRelative bool `json:"day_is_relative"`
}

type intents struct {
	Schedule scheduleIntents `json:"schedule"`
}

type scheduleIntents struct {
	Slots slots `json:"slots"`
}

type slots struct {
	When whenSlot `json:"when"`
}

type whenSlot struct {
	Type  string         `json:"type"`
	Value yandexDatetime `json:"value"`
}

type nlu struct {
	Entities []entity `json:"entities"`
	Tokens   []string `json:"tokens"`
	Intents  intents  `json:"intents"`
}

type request struct {
	NLU nlu `json:"nlu"`
}
