import { apiClient } from './client';
import type { Candidate } from '../types/candidate';

export async function fetchCandidates() {
  const { data } = await apiClient.get<Candidate[]>('/candidates');
  return data;
}

export type CandidateCreatePayload = {
  name: string;
  phone?: string;
  email?: string;
  current_company?: string;
  current_title?: string;
  years_of_experience?: number;
  source?: string;
  status?: string;
  tags?: string[];
};

export async function createCandidate(payload: CandidateCreatePayload) {
  const { data } = await apiClient.post<Candidate>('/candidates', payload);
  return data;
}
