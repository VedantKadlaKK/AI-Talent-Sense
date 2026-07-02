export type JobStatus = "draft" | "analyzed" | "searching" | "ranked" | "archived";

export interface Job {
  id: number;
  title: string;
  company_name: string;
  description: string;
  status: JobStatus;
  created_at: string;
  updated_at: string;
  intelligence: JobIntelligence | null;
}

export interface JobCreatePayload {
  title: string;
  company_name: string;
  description: string;
  status: JobStatus;
}

export interface JobIntelligence {
  id: number;
  job_id: number;
  skills: string[];
  experience: string;
  education: string;
  industry: string;
  location: string;
  seniority: string;
  certifications: string[];
  nice_to_have_skills: string[];
  raw_ai_output: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CandidateSource {
  id: number;
  source: string;
  external_id: string;
  profile_url: string;
  created_at: string;
}

export interface CandidateProfile {
  id: number;
  skills: string[];
  projects: Array<Record<string, unknown>>;
  education: string[];
  certifications: string[];
  github_username: string;
  portfolio_url: string;
  resume_path: string;
  normalized_summary: string | null;
  source_coverage: Record<string, unknown> | null;
  resume_insights: Record<string, unknown> | null;
  github_insights: Record<string, unknown> | null;
  portfolio_insights: Record<string, unknown> | null;
  api_insights: Record<string, unknown> | null;
  normalized_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Candidate {
  id: number;
  full_name: string;
  email: string;
  phone: string;
  location: string;
  summary: string;
  experience: string;
  current_company: string;
  sources: CandidateSource[];
  profile: CandidateProfile | null;
  created_at: string;
  updated_at: string;
}

export interface CandidateSearchResponse {
  job_id: number;
  source_count: number;
  candidate_count: number;
  candidates: Candidate[];
}

export interface CandidateIntelligenceBatchResponse {
  job_id: number;
  normalized_count: number;
  candidates: Candidate[];
}

export interface Signal {
  id: number;
  name: string;
  category: string;
  description: string;
  default_weight: number;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface SignalResult {
  id: number;
  candidate_id: number;
  job_id: number;
  signal_id: number;
  signal_name: string;
  category: string;
  score: number;
  weight: number;
  contribution: number;
  reason: string;
  created_at: string;
  updated_at: string;
}

export interface CandidateSignalEvaluation {
  candidate_id: number;
  result_count: number;
  results: SignalResult[];
}

export interface SignalEvaluationResponse {
  job_id: number;
  candidate_count: number;
  signal_count: number;
  results: CandidateSignalEvaluation[];
}

export interface Recommendation {
  id: number;
  candidate_id: number;
  job_id: number;
  overall_score: number;
  rank: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  missing_skills: string[];
  recommendation: string;
  raw_ai_output: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface RecommendationCandidate {
  recommendation: Recommendation;
  candidate: Candidate;
  signals: SignalResult[];
}

export interface RecommendationResponse {
  job_id: number;
  recommendation_count: number;
  recommendations: RecommendationCandidate[];
}
