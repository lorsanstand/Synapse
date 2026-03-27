package yandex

import (
	"fmt"

	"github.com/lorsanstand/yandex_service/internal/integration/schedule"
)

type responseResponse struct {
	Text       string `json:"text"`
	TTS        string `json:"tts"`
	EndSession bool   `json:"end_session"`
}

type YandexResponse struct {
	Response        responseResponse `json:"response"`
	SessionState    map[string]any   `json:"session_state"`
	UserStateUpdate map[string]any   `json:"user_state_update"`
	Version         string           `json:"version"`
}

func failedYandexResponse() YandexResponse {
	return YandexResponse{
		Response: responseResponse{
			Text:       "Простите произошла ошибка в навыке, попробуйте позже",
			TTS:        "Ой, кажется, мои шестерёнки немного заело. Приношу извинения! Попробуйте зайти чуть позже.",
			EndSession: true,
		},
		Version: "1.0",
	}
}

func scheduleYandexResponse(schedule schedule.Day) YandexResponse {
	var text string

	text = fmt.Sprintf("На заданный день у вас %v пары, ", len(schedule.Pairs))
	for _, pair := range schedule.Pairs {
		//tim := strings.Split(pair[0].Time, " - ")
		//text += fmt.Sprintf("Первая пара начинается в %v.", tim[0])

		text += fmt.Sprintf("%v, ", pair[0].LessonName)
	}

	if schedule.Pairs == nil {
		text = "Хорошие новости! Сегодня пар нет, можно отдыхать."
	}

	return YandexResponse{
		Response: responseResponse{
			Text:       text,
			TTS:        text,
			EndSession: true,
		},
		Version: "1.0",
	}
}
