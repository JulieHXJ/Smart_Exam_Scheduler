from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from app.auth.core import (
    get_current_user, logout, request_code, verify_code,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

class EmailRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)

class VerifyRequest(EmailRequest):
    code: str = Field(pattern=r"^[A-Za-z0-9]{6}$")

@router.post("/request-code")
def request_login_code(payload: EmailRequest, request: Request):
    # Generic response to avoid leaking permitted account addresses.
    request_code(payload.email, request.client.host if request.client else "unknown")
    return {"message": "If this address is authorized, a code has been sent."}

@router.post("/verify-code")
def verify_login_code(payload: VerifyRequest, request: Request, response: Response):
    token = verify_code(payload.email, payload.code, request.client.host if request.client else "unknown")
    response.set_cookie(
        "smart_exam_session", token, httponly=True,
        secure=__import__('os').getenv("AUTH_SECURE_COOKIE", "true").lower() == "true",
        samesite="lax", max_age=8 * 60 * 60, path="/",
    )
    return {"message": "Signed in"}

@router.get("/me")
def current_user(user=Depends(get_current_user)):
    return user

@router.post("/logout")
def sign_out(request: Request, response: Response):
    logout(request.cookies.get("smart_exam_session"))
    response.delete_cookie("smart_exam_session", path="/")
    return {"message": "Signed out"}
