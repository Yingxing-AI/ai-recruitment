from fastapi import APIRouter
from pydantic import BaseModel

from app.core.security import create_access_token

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(payload: LoginRequest) -> dict[str, str]:
    return {
        "access_token": create_access_token(payload.email),
        "token_type": "bearer",
    }
