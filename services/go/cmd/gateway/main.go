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

	"github.com/sentinel/services/go/internal/middleware"
	"github.com/sentinel/services/go/internal/system"
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

	coreAddr := os.Getenv("CORE_ADDR")
	if coreAddr == "" {
		coreAddr = "core:9000"
	}

	initCoreClient(coreAddr)

	upstream, err := url.Parse(target)
	if err != nil {
		log.Fatalf("invalid upstream URL %q: %v", target, err)
	}

	restProxy := httputil.NewSingleHostReverseProxy(upstream)

	wsProxy := &httputil.ReverseProxy{
		Rewrite: func(r *httputil.ProxyRequest) {
			r.SetURL(upstream)
			r.Out.URL.Path = strings.Replace(r.In.URL.Path, "/ws/", "/api/v1/ws/", 1)
			r.Out.URL.RawPath = strings.Replace(r.In.URL.RawPath, "/ws/", "/api/v1/ws/", 1)
			r.Out.Host = r.In.Host
		},
	}

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

	mux.HandleFunc("GET /api/v1/system/version", system.VersionHandler)
	mux.HandleFunc("GET /api/v1/system/status", system.StatusHandler)

	// Native world-state WebSocket served directly by gateway (strangler fig)
	mux.HandleFunc("/ws/world-state", worldStateHandler)

	mux.HandleFunc("/api/v1/health/live", proxyHandler(restProxy))
	mux.HandleFunc("/api/v1/health/ready", proxyHandler(restProxy))
	mux.HandleFunc("/api/v1/", proxyHandler(restProxy))

	// Generic WS proxy for all Python WS endpoints
	mux.HandleFunc("/ws/", proxyHandler(wsProxy))

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		http.NotFound(w, r)
	})

	rl := middleware.NewRateLimiter(100, 10*time.Second)

	srv := &http.Server{
		Addr:    ":" + port,
		Handler: rl.Middleware(middleware.CORS(middleware.RequestID(middleware.Auth(withLogging(mux))))),
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		log.Printf("gateway listening on :%s, proxying to %s, core at %s", port, target, coreAddr)
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
