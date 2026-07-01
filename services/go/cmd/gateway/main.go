package main

import (
	"context"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"
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

	restProxy := httputil.NewSingleHostReverseProxy(upstream)
	wsProxy := httputil.NewSingleHostReverseProxy(upstream)

	mux := http.NewServeMux()

	mux.HandleFunc("GET /health/live", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"ok","service":"gateway"}`))
	})

	mux.HandleFunc("GET /health/ready", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"ok","service":"gateway"}`))
	})

	mux.HandleFunc("/api/v1/health/live", proxyHandler(restProxy))
	mux.HandleFunc("/api/v1/health/ready", proxyHandler(restProxy))
	mux.HandleFunc("/api/v1/", proxyHandler(restProxy))

	mux.HandleFunc("/ws/", proxyHandler(wsProxy))

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		http.NotFound(w, r)
	})

	srv := &http.Server{
		Addr:         ":" + port,
		Handler:      withLogging(mux),
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		log.Printf("gateway listening on :%s, proxying to %s", port, target)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("gateway: %v", err)
		}
	}()

	<-quit
	log.Println("gateway: shutting down")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("gateway: forced shutdown: %v", err)
	}

	log.Println("gateway: stopped")
}

func proxyHandler(proxy *httputil.ReverseProxy) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		proxy.ServeHTTP(w, r)
	}
}

func withLogging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		contentType := r.Header.Get("Content-Type")
		if strings.Contains(contentType, "text/event-stream") || r.Header.Get("Upgrade") == "websocket" {
			next.ServeHTTP(w, r)
			log.Printf("%s %s %s %v [stream]", r.Method, r.URL.Path, r.RemoteAddr, time.Since(start))
			return
		}

		lrw := &loggingResponseWriter{ResponseWriter: w, statusCode: http.StatusOK}
		next.ServeHTTP(lrw, r)
		log.Printf("%s %s %s %d %v", r.Method, r.URL.Path, r.RemoteAddr, lrw.statusCode, time.Since(start))
	})
}

type loggingResponseWriter struct {
	http.ResponseWriter
	statusCode int
}

func (lrw *loggingResponseWriter) WriteHeader(code int) {
	lrw.statusCode = code
	lrw.ResponseWriter.WriteHeader(code)
}
