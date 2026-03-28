package yandex

import (
	"fmt"
	"log/slog"
	"strconv"
	"strings"

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
	var text, lessons, FirstPair string
	NumPairSmall := 10

	text = fmt.Sprintf("В %v у вас %v пары, ", schedule.DayWeek, len(schedule.Pairs))
	for num, pair := range schedule.Pairs {
		numPair, err := strconv.Atoi(num)
		if err != nil {
			slog.Warn("Failed convert string to int")
		}

		if numPair < NumPairSmall {
			tim := strings.Split(pair[0].Time, " - ")
			FirstPair = fmt.Sprintf("Первая пара начинается в %v.", tim[0])
			NumPairSmall = numPair
		}

		lessons += fmt.Sprintf("%v, ", strings.Trim(pair[0].LessonName, "_"))
	}

	text = text + lessons + FirstPair

	if schedule.Pairs == nil {
		text = "Хорошие новости! пар нет, можно отдыхать."
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
