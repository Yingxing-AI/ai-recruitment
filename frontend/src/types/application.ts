export interface Application {
  id: number;
  job_id: number;
  candidate_id: number;
  current_stage: string;
  status: string;
  source?: string;
  owner_user_id?: number;
  applied_at: string;
  created_at: string;
  updated_at: string;
}
