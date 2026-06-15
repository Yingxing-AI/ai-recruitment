import { apiClient } from './client';
import type { Job } from '../types/job';

export async function fetchJobs() {
  const { data } = await apiClient.get<Job[]>('/jobs');
  return data;
}
