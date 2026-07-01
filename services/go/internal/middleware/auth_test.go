package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestAuthAnonymous(t *testing.T) {
	handler := Auth(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		user := r.Context().Value(UserContextKey).(*UserContext)
		if user.UserID != "anonymous" {
			t.Fatalf("expected anonymous, got %q", user.UserID)
		}
		if user.Role != "viewer" {
			t.Fatalf("expected viewer role, got %q", user.Role)
		}
		w.WriteHeader(http.StatusOK)
	}))

	req := httptest.NewRequest("GET", "/", nil)
	w := httptest.NewRecorder()
	handler.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", w.Code)
	}
}

func TestAuthWithBearer(t *testing.T) {
	handler := Auth(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		user := r.Context().Value(UserContextKey).(*UserContext)
		if user.UserID != "user-001" {
			t.Fatalf("expected user-001, got %q", user.UserID)
		}
		if r.Header.Get("X-User-ID") != "user-001" {
			t.Fatal("expected X-User-ID header")
		}
		w.WriteHeader(http.StatusOK)
	}))

	req := httptest.NewRequest("GET", "/", nil)
	req.Header.Set("Authorization", "Bearer some-valid-token")
	w := httptest.NewRecorder()
	handler.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", w.Code)
	}
}
