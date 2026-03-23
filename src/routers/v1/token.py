from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.schemas import TokenRequest, TokenResponse
from src.services import AuthService, create_access_token

token_router = APIRouter(prefix="/token", tags=["token"])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@token_router.post("/", response_model=TokenResponse)
async def login_for_access_token(data: TokenRequest, session: DBSession):
    seller = await AuthService(session).authenticate(data.e_mail, data.password)
    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(seller.e_mail),
        "token_type": "bearer",
    }