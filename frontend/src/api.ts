import type {
  Candidate,
  CandidateIntelligenceBatchResponse,
  CandidateSearchResponse,
  Job,
  JobCreatePayload,
  JobIntelligence,
  RecommendationResponse,
  Signal,
  SignalEvaluationResponse,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const jobsApi = {
  list: () => request<Job[]>("/jobs"),
  get: (id: number) => request<Job>(`/jobs/${id}`),
  create: (payload: JobCreatePayload) =>
    request<Job>("/jobs", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  delete: (id: number) =>
    request<void>(`/jobs/${id}`, {
      method: "DELETE",
    }),
  analyze: (id: number) =>
    request<JobIntelligence>(`/jobs/${id}/analyze`, {
      method: "POST",
    }),
  searchCandidates: (id: number) =>
    request<CandidateSearchResponse>(`/jobs/${id}/search`, {
      method: "POST",
    }),
  normalizeCandidates: (id: number) =>
    request<CandidateIntelligenceBatchResponse>(`/jobs/${id}/normalize-candidates`, {
      method: "POST",
    }),
  evaluateSignals: (id: number) =>
    request<SignalEvaluationResponse>(`/jobs/${id}/evaluate-signals`, {
      method: "POST",
    }),
  signalResults: (id: number) => request<SignalEvaluationResponse>(`/jobs/${id}/signal-results`),
  rankCandidates: (id: number) =>
    request<RecommendationResponse>(`/jobs/${id}/rank`, {
      method: "POST",
    }),
  recommendations: (id: number) => request<RecommendationResponse>(`/recommendations/${id}`),
};

export const candidatesApi = {
  list: () => request<Candidate[]>("/candidates"),
  get: (id: number) => request<Candidate>(`/candidates/${id}`),
  normalize: (id: number) =>
    request<Candidate>(`/candidates/${id}/normalize`, {
      method: "POST",
    }),
};

export const signalsApi = {
  list: () => request<Signal[]>("/signals"),
};
