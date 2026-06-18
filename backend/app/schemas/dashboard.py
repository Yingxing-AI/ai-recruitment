from pydantic import BaseModel


class DashboardFunnelItem(BaseModel):
    stage: str
    label: str
    count: int


class DashboardSummaryRead(BaseModel):
    job_count: int
    candidate_count: int
    resume_count: int
    interviewing_count: int
    offer_count: int
    hired_count: int
    funnel: list[DashboardFunnelItem]
