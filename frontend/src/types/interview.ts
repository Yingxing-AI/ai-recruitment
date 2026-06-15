export interface Interview {
  id: number;
  application_id: number;
  job_id: number;
  candidate_id: number;
  round: number;
  interview_type: string;
  scheduled_start_at?: string;
  scheduled_end_at?: string;
  location?: string;
  meeting_link?: string;
  status: string;
  created_at: string;
  updated_at: string;
}
