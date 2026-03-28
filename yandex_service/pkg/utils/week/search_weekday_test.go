package week

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestSearchDay(t *testing.T) {
	num, ok := SearchDay("Среду")
	if !ok {
		t.Fatal("failed ok")
	}

	assert.Equal(t, num, 3)
}
