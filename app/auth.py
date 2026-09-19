from fastapi import HTTPException, Request

from app.config import settings


async def require_api_key(request: Request) -> None:
    key = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    if not key or key != settings.registry_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
