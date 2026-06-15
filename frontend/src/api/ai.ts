import { apiClient } from './client';
import type { AIResumeAnalysis, JobMatchScore, ParsedResumeResult } from '../types/ai';

export async function parseResume(resumeId: number) {
  const { data } = await apiClient.post<ParsedResumeResult>(`/ai/resumes/${resumeId}/parse`);
  return data;
}

export async function summarizeResume(resumeId: number) {
  const { data } = await apiClient.post<AIResumeAnalysis>(`/ai/resumes/${resumeId}/summary`);
  return data;
}

export async function matchCandidate(payload: { jobId: number; candidateId: number }) {
  const { data } = await apiClient.post<JobMatchScore>(
    `/ai/jobs/${payload.jobId}/candidates/${payload.candidateId}/match`
  );
  return data;
}

export async function generateInterviewQuestions(payload: { jobId: number; candidateId: number }) {
  const { data } = await apiClient.post<AIResumeAnalysis>(
    `/ai/jobs/${payload.jobId}/candidates/${payload.candidateId}/interview-questions`
  );
  return data;
}

export async function fetchAnalyses() {
  const { data } = await apiClient.get<AIResumeAnalysis[]>('/ai/analyses');
  return data;
}

export async function fetchMatches() {
  const { data } = await apiClient.get<JobMatchScore[]>('/ai/matches');
  return data;
}
