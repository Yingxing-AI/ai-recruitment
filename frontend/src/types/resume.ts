export interface Resume {
  id: number;
  candidate_id: number;
  file_name: string;
  file_path: string;
  file_type?: string;
  file_size?: number;
  raw_text?: string;
  parse_status: string;
  parse_error?: string;
  created_at: string;
  updated_at: string;
}
