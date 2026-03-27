package respond

import (
	"encoding/json"
	"net/http"
)

type Respond struct {
}

func (r Respond) RespondJSON(w http.ResponseWriter, status int, data any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if data != nil {
		json.NewEncoder(w).Encode(data)
	}
}
