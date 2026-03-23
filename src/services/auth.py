from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.configurations.settings import settings
from src.models.sellers import Seller

__all__ = [
    "AuthService",
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "get_current_seller",
]

password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer()

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": subject,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def authenticate(self, e_mail: str, password: str) -> Seller | None:
        query = select(Seller).where(Seller.e_mail == e_mail)
        result = await self.session.execute(query)
        seller = result.scalar_one_or_none()

        if seller is None:
            return None

        if not verify_password(password, seller.password):
            return None

        return seller


async def get_current_seller(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: DBSession,
) -> Seller:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        e_mail = payload.get("sub")
        if e_mail is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    query = select(Seller).where(Seller.e_mail == e_mail)
    result = await session.execute(query)
    seller = result.scalar_one_or_none()

    if seller is None:
        raise credentials_exception

    return seller