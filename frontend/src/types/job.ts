export interface Job {
  id: number;
  title: string;
  location?: string;
  headcount: number;
  status: string;
  jd_text: string;
  requirements_text?: string;
  created_at: string;
  updated_at: string;
}
