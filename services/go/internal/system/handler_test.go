package system

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestVersionHandler(t *testing.T) {
	req := httptest.NewRequest("GET", "/api/v1/system/version", nil)
	w := httptest.NewRecorder()
	VersionHandler(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", w.Code)
	}

	var info VersionInfo
	if err := json.NewDecoder(w.Body).Decode(&info); err != nil {
		t.Fatalf("json decode: %v", err)
	}
	if info.Version != "0.1.0" {
		t.Fatalf("expected version 0.1.0, got %q", info.Version)
	}
	if info.GoVersion == "" {
		t.Fatal("expected non-empty go_version")
	}
}

func TestStatusHandler(t *testing.T) {
	req := httptest.NewRequest("GET", "/api/v1/system/status", nil)
	w := httptest.NewRecorder()
	StatusHandler(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", w.Code)
	}

	var status StatusInfo
	if err := json.NewDecoder(w.Body).Decode(&status); err != nil {
		t.Fatalf("json decode: %v", err)
	}
	if status.GoVersion == "" {
		t.Fatal("expected non-empty go_version")
	}
	if status.Goroutines <= 0 {
		t.Fatal("expected positive goroutines")
	}
}
