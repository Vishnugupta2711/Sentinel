package system

import (
	"encoding/json"
	"net/http"
	"runtime"
	"runtime/debug"
	"time"
)

var startTime = time.Now()

type VersionInfo struct {
	Version   string `json:"version"`
	Commit    string `json:"commit"`
	GoVersion string `json:"go_version"`
}

type StatusInfo struct {
	Uptime    string  `json:"uptime"`
	GoVersion string  `json:"go_version"`
	Goroutines int    `json:"goroutines"`
	MemoryMB  float64 `json:"memory_mb"`
}

func VersionHandler(w http.ResponseWriter, r *http.Request) {
	info := VersionInfo{
		Version:   "0.1.0",
		Commit:    func() string { s, _ := debug.ReadBuildInfo(); return s.Main.Version }(),
		GoVersion: runtime.Version(),
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(info)
}

func StatusHandler(w http.ResponseWriter, r *http.Request) {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	status := StatusInfo{
		Uptime:    time.Since(startTime).Round(time.Second).String(),
		GoVersion: runtime.Version(),
		Goroutines: runtime.NumGoroutine(),
		MemoryMB:  float64(m.Alloc) / 1024 / 1024,
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}
