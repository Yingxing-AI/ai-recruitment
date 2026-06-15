export interface Candidate {
  id: number;
  name: string;
  phone?: string;
  email?: string;
  current_company?: string;
  current_title?: string;
  years_of_experience?: number;
  source?: string;
  status: string;
  created_at: string;
  updated_at: string;
}
