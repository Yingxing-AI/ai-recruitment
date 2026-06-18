export interface DashboardFunnelItem {
  stage: string;
  label: string;
  count: number;
}

export interface DashboardSummary {
  job_count: number;
  candidate_count: number;
  resume_count: number;
  interviewing_count: number;
  offer_count: number;
  hired_count: number;
  funnel: DashboardFunnelItem[];
}
