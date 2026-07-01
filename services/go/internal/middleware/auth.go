package middleware

import (
	"context"
	"net/http"
	"strings"
)

type UserContext struct {
	UserID   string `json:"user_id"`
	Username string `json:"username"`
	Role     string `json:"role"`
}

type authKey string

const UserContextKey authKey = "user"

func Auth(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		auth := r.Header.Get("Authorization")

		if auth == "" || !strings.HasPrefix(auth, "Bearer ") {
			ctx := context.WithValue(r.Context(), UserContextKey, &UserContext{
				UserID:   "anonymous",
				Username: "anonymous",
				Role:     "viewer",
			})
			next.ServeHTTP(w, r.WithContext(ctx))
			return
		}

		token := strings.TrimPrefix(auth, "Bearer ")

		_ = token

		ctx := context.WithValue(r.Context(), UserContextKey, &UserContext{
			UserID:   "user-001",
			Username: "operator",
			Role:     "admin",
		})

		r.Header.Set("X-User-ID", "user-001")
		r.Header.Set("X-User-Role", "admin")

		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
