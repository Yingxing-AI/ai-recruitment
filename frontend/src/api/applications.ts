import { apiClient } from './client';
import type { Application } from '../types/application';

export type ApplicationCreatePayload = {
  job_id: number;
  candidate_id: number;
  source?: string;
  owner_user_id?: number;
};

export async function fetchApplications() {
  const { data } = await apiClient.get<Application[]>('/applications');
  return data;
}

export async function createApplication(payload: ApplicationCreatePayload) {
  const { data } = await apiClient.post<Application>('/applications', payload);
  return data;
}

export async function updateApplicationStage(
  applicationId: number,
  payload: { to_stage: string; reason?: string }
) {
  const { data } = await apiClient.post<Application>(`/applications/${applicationId}/stage`, payload);
  return data;
}
