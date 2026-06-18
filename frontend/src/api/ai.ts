import { apiClient } from './client';
import type {
  AuditLog,
  AIResumeAnalysis,
  JobMatchScore,
  ParsedResumeResult,
  WorkflowInterpretRequest,
  WorkflowInterpretResult
} from '../types/ai';

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

export async function fetchAnalysesByCandidate(candidateId: number) {
  const { data } = await apiClient.get<AIResumeAnalysis[]>('/ai/analyses', { params: { candidate_id: candidateId } });
  return data;
}

export async function fetchMatches() {
  const { data } = await apiClient.get<JobMatchScore[]>('/ai/matches');
  return data;
}

export async function fetchMatchesByFilters(params?: { jobId?: number; candidateId?: number }) {
  const { data } = await apiClient.get<JobMatchScore[]>('/ai/matches', {
    params: {
      job_id: params?.jobId,
      candidate_id: params?.candidateId
    }
  });
  return data;
}

export async function interpretWorkflow(payload: WorkflowInterpretRequest) {
  const { data } = await apiClient.post<WorkflowInterpretResult>('/ai/workflows/interpret', payload);
  return data;
}

export async function fetchAuditLogs(params?: { targetType?: string; targetId?: number; action?: string; limit?: number }) {
  const { data } = await apiClient.get<AuditLog[]>('/audit-logs', {
    params: {
      target_type: params?.targetType,
      target_id: params?.targetId,
      action: params?.action,
      limit: params?.limit
    }
  });
  return data;
}
