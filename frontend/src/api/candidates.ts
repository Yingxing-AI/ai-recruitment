import { apiClient } from './client';
import type { Candidate } from '../types/candidate';

export async function fetchCandidates() {
  const { data } = await apiClient.get<Candidate[]>('/candidates');
  return data;
}
