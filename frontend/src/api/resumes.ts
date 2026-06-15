import { apiClient } from './client';
import type { Resume } from '../types/resume';

export async function fetchResumes() {
  const { data } = await apiClient.get<Resume[]>('/resumes');
  return data;
}

export async function uploadResume(payload: { candidate_id: number; file: File; raw_text?: string }) {
  const formData = new FormData();
  formData.append('candidate_id', String(payload.candidate_id));
  formData.append('file', payload.file);
  if (payload.raw_text) {
    formData.append('raw_text', payload.raw_text);
  }

  const { data } = await apiClient.post<Resume>('/resumes/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
}
