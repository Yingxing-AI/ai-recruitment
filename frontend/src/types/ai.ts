export interface ParsedResumeResult {
  resume_id: number;
  candidate_id: number;
  parsed_json: Record<string, unknown>;
  raw_text?: string;
  parse_status: string;
}

export interface AIResumeAnalysis {
  id: number;
  candidate_id: number;
  resume_id: number;
  summary?: string;
  skills_json?: unknown[];
  work_experience_summary?: string;
  project_experience_summary?: string;
  education_summary?: string;
  strengths_json?: unknown[];
  risks_json?: unknown[];
  interview_questions_json?: Array<{ type: string; question: string; focus: string }>;
  raw_response?: Record<string, unknown>;
  model_provider?: string;
  model_name?: string;
  status: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface JobMatchScore {
  id: number;
  job_id: number;
  candidate_id: number;
  application_id?: number;
  total_score?: string;
  level?: string;
  dimension_scores_json?: Record<string, number>;
  matched_points_json?: unknown[];
  missing_points_json?: unknown[];
  risk_points_json?: unknown[];
  recommendation?: string;
  explanation?: string;
  raw_response?: Record<string, unknown>;
  model_provider?: string;
  model_name?: string;
  status: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}
