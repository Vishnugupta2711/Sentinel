package main

import (
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
)

func main() {
	port := os.Getenv("GATEWAY_PORT")
	if port == "" {
		port = "8080"
	}

	target := os.Getenv("UPSTREAM_URL")
	if target == "" {
		target = "http://backend:8000"
	}

	upstream, err := url.Parse(target)
	if err != nil {
		log.Fatalf("invalid upstream URL %q: %v", target, err)
	}

	proxy := httputil.NewSingleHostReverseProxy(upstream)

	mux := http.NewServeMux()
	mux.HandleFunc("/health/live", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"ok"}`))
	})
	mux.HandleFunc("/health/ready", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"ok"}`))
	})
	mux.Handle("/", proxy)

	log.Printf("gateway listening on :%s, proxying to %s", port, target)
	if err := http.ListenAndServe(":"+port, mux); err != nil {
		log.Fatalf("gateway: %v", err)
	}
}
