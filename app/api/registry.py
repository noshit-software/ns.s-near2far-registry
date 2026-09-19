import re
import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app import cloudflare
from app.auth import require_api_key
from app.db import get_db

router = APIRouter()

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,28}[a-z0-9]$")

RESERVED = {
    "www", "api", "registry", "gps", "mail", "near2far",
    "gardunia", "admin", "help", "support", "status",
}


def _validate_slug(slug: str) -> None:
    if not SLUG_RE.match(slug):
        raise HTTPException(status_code=400, detail="Slug must be 3-30 chars, lowercase alphanumeric and hyphens, no leading/trailing hyphens")
    if slug in RESERVED:
        raise HTTPException(status_code=400, detail="Slug is reserved")


class RegisterRequest(BaseModel):
    slug: str
    ip: str


class UpdateRequest(BaseModel):
    slug: str
    ip: str
    token: str


@router.get("/check/{slug}")
async def check_slug(slug: str, db=Depends(get_db)) -> dict:
    _validate_slug(slug)
    row = await db.execute("SELECT slug FROM registrations WHERE slug = ?", (slug,))
    taken = await row.fetchone() is not None
    return {"success": True, "data": {"slug": slug, "available": not taken}}


@router.post("/register", dependencies=[Depends(require_api_key)])
async def register(body: RegisterRequest, db=Depends(get_db)) -> dict:
    _validate_slug(body.slug)

    row = await db.execute("SELECT slug FROM registrations WHERE slug = ?", (body.slug,))
    if await row.fetchone():
        raise HTTPException(status_code=409, detail="Slug already registered")

    token = secrets.token_urlsafe(32)
    await cloudflare.create_record(body.slug, body.ip)
    await db.execute(
        "INSERT INTO registrations (slug, ip, token) VALUES (?, ?, ?)",
        (body.slug, body.ip, token),
    )
    await db.commit()

    return {"success": True, "data": {"slug": body.slug, "token": token}}


@router.post("/update")
async def update(body: UpdateRequest, db=Depends(get_db)) -> dict:
    row = await db.execute("SELECT token FROM registrations WHERE slug = ?", (body.slug,))
    record = await row.fetchone()
    if not record:
        raise HTTPException(status_code=404, detail="Slug not registered")
    if not secrets.compare_digest(record["token"], body.token):
        raise HTTPException(status_code=401, detail="Invalid token")

    await cloudflare.update_record(body.slug, body.ip)
    await db.execute(
        "UPDATE registrations SET ip = ?, updated_at = datetime('now') WHERE slug = ?",
        (body.ip, body.slug),
    )
    await db.commit()
    return {"success": True, "data": None}


@router.delete("/delete", dependencies=[Depends(require_api_key)])
async def delete_slug(body: UpdateRequest, db=Depends(get_db)) -> dict:
    row = await db.execute("SELECT slug FROM registrations WHERE slug = ?", (body.slug,))
    if not await row.fetchone():
        raise HTTPException(status_code=404, detail="Slug not registered")

    await cloudflare.delete_record(body.slug)
    await db.execute("DELETE FROM registrations WHERE slug = ?", (body.slug,))
    await db.commit()
    return {"success": True, "data": None}
