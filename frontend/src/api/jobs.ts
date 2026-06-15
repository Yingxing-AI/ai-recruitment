import { apiClient } from './client';
import type { Job } from '../types/job';

export async function fetchJobs() {
  const { data } = await apiClient.get<Job[]>('/jobs');
  return data;
}

export type JobCreatePayload = {
  title: string;
  location?: string;
  headcount?: number;
  employment_type?: string;
  jd_text: string;
  requirements_text?: string;
  status?: string;
};

export async function createJob(payload: JobCreatePayload) {
  const { data } = await apiClient.post<Job>('/jobs', payload);
  return data;
}
