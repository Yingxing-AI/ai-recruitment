from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.candidate import Candidate, CandidateTag
from app.schemas.candidate import CandidateCreate, CandidateRead, CandidateUpdate

router = APIRouter()


@router.get("", response_model=list[CandidateRead])
def list_candidates(
    keyword: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Candidate]:
    stmt = select(Candidate).order_by(Candidate.created_at.desc())
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(
            or_(
                Candidate.name.ilike(like),
                Candidate.phone.ilike(like),
                Candidate.email.ilike(like),
                Candidate.current_company.ilike(like),
            )
        )
    return list(db.scalars(stmt).all())


@router.post("", response_model=CandidateRead)
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)) -> Candidate:
    data = payload.model_dump(exclude={"tags"})
    candidate = Candidate(**data)
    db.add(candidate)
    db.flush()
    for tag in payload.tags:
        db.add(CandidateTag(candidate_id=candidate.id, tag=tag))
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/{candidate_id}", response_model=CandidateRead)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.patch("/{candidate_id}", response_model=CandidateRead)
def update_candidate(
    candidate_id: int,
    payload: CandidateUpdate,
    db: Session = Depends(get_db),
) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(candidate, key, value)
    db.commit()
    db.refresh(candidate)
    return candidate
