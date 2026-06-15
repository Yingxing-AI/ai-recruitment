import { apiClient } from './client';
import type { Interview } from '../types/interview';

export type InterviewCreatePayload = {
  application_id: number;
  job_id: number;
  candidate_id: number;
  round?: number;
  interview_type?: string;
  scheduled_start_at?: string;
  scheduled_end_at?: string;
  location?: string;
  meeting_link?: string;
  interviewer_ids?: number[];
};

export async function fetchInterviews() {
  const { data } = await apiClient.get<Interview[]>('/interviews');
  return data;
}

export async function createInterview(payload: InterviewCreatePayload) {
  const { data } = await apiClient.post<Interview>('/interviews', payload);
  return data;
}
