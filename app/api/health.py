from fastapi import APIRouter, Depends

from app.db import get_db

router = APIRouter()


@router.get("/health")
async def health(db=Depends(get_db)) -> dict:
    row = await db.execute("SELECT 1")
    await row.fetchone()
    return {"success": True, "data": {"status": "ok"}}
