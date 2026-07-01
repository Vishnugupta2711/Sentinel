package main

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"
	"strings"

	pbwk "github.com/sentinel/services/go/pkg/proto/worker"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

func listWorkersHandler(w http.ResponseWriter, r *http.Request) {
	if workerClient == nil {
		writeJSON(w, http.StatusServiceUnavailable, map[string]string{"error": "core not available"})
		return
	}

	page, _ := strconv.Atoi(r.URL.Query().Get("page"))
	pageSize, _ := strconv.Atoi(r.URL.Query().Get("page_size"))
	role := r.URL.Query().Get("role")
	statusFilter := r.URL.Query().Get("status")
	zoneID := r.URL.Query().Get("zone_id")

	resp, err := workerClient.ListWorkers(r.Context(), &pbwk.ListWorkersRequest{
		Page:     int32(page),
		PageSize: int32(pageSize),
		Role:     role,
		Status:   statusFilter,
		ZoneId:   zoneID,
	})
	if err != nil {
		log.Printf("gateway: ListWorkers error: %v", err)
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "failed to list workers"})
		return
	}

	writeJSON(w, http.StatusOK, resp)
}

func getWorkerHandler(w http.ResponseWriter, r *http.Request) {
	if workerClient == nil {
		writeJSON(w, http.StatusServiceUnavailable, map[string]string{"error": "core not available"})
		return
	}

	id := strings.TrimPrefix(r.URL.Path, "/api/v1/workers/")
	if id == "" || id == r.URL.Path {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "missing worker id"})
		return
	}

	resp, err := workerClient.GetWorker(r.Context(), &pbwk.GetWorkerRequest{Id: id})
	if err != nil {
		st, ok := status.FromError(err)
		if ok && st.Code() == codes.NotFound {
			writeJSON(w, http.StatusNotFound, map[string]string{"error": "worker not found"})
			return
		}
		log.Printf("gateway: GetWorker error: %v", err)
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "failed to get worker"})
		return
	}

	writeJSON(w, http.StatusOK, resp.Worker)
}

func createWorkerHandler(w http.ResponseWriter, r *http.Request) {
	if workerClient == nil {
		writeJSON(w, http.StatusServiceUnavailable, map[string]string{"error": "core not available"})
		return
	}

	var req pbwk.CreateWorkerRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}

	resp, err := workerClient.CreateWorker(r.Context(), &req)
	if err != nil {
		log.Printf("gateway: CreateWorker error: %v", err)
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "failed to create worker"})
		return
	}

	writeJSON(w, http.StatusCreated, resp.Worker)
}

func updateWorkerHandler(w http.ResponseWriter, r *http.Request) {
	if workerClient == nil {
		writeJSON(w, http.StatusServiceUnavailable, map[string]string{"error": "core not available"})
		return
	}

	id := strings.TrimPrefix(r.URL.Path, "/api/v1/workers/")
	if id == "" || id == r.URL.Path {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "missing worker id"})
		return
	}

	var req pbwk.UpdateWorkerRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}
	req.Id = id

	resp, err := workerClient.UpdateWorker(r.Context(), &req)
	if err != nil {
		st, ok := status.FromError(err)
		if ok && st.Code() == codes.NotFound {
			writeJSON(w, http.StatusNotFound, map[string]string{"error": "worker not found"})
			return
		}
		log.Printf("gateway: UpdateWorker error: %v", err)
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "failed to update worker"})
		return
	}

	writeJSON(w, http.StatusOK, resp.Worker)
}

func deleteWorkerHandler(w http.ResponseWriter, r *http.Request) {
	if workerClient == nil {
		writeJSON(w, http.StatusServiceUnavailable, map[string]string{"error": "core not available"})
		return
	}

	id := strings.TrimPrefix(r.URL.Path, "/api/v1/workers/")
	if id == "" || id == r.URL.Path {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "missing worker id"})
		return
	}

	_, err := workerClient.DeleteWorker(r.Context(), &pbwk.DeleteWorkerRequest{Id: id})
	if err != nil {
		st, ok := status.FromError(err)
		if ok && st.Code() == codes.NotFound {
			writeJSON(w, http.StatusNotFound, map[string]string{"error": "worker not found"})
			return
		}
		log.Printf("gateway: DeleteWorker error: %v", err)
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "failed to delete worker"})
		return
	}

	writeJSON(w, http.StatusNoContent, nil)
}

func writeJSON(w http.ResponseWriter, statusCode int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	if v != nil {
		json.NewEncoder(w).Encode(v)
	}
}
