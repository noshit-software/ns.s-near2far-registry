import httpx

from app.config import settings

_CF_BASE = "https://api.cloudflare.com/client/v4"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.cloudflare_api_token}"}


async def _get_record_id(slug: str) -> str | None:
    name = f"{slug}.{settings.cloudflare_domain}"
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{_CF_BASE}/zones/{settings.cloudflare_zone_id}/dns_records",
            params={"type": "A", "name": name},
            headers=_headers(),
        )
        r.raise_for_status()
        records = r.json()["result"]
        return records[0]["id"] if records else None


async def create_record(slug: str, ip: str) -> None:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_CF_BASE}/zones/{settings.cloudflare_zone_id}/dns_records",
            json={"type": "A", "name": f"{slug}.{settings.cloudflare_domain}", "content": ip, "proxied": True},
            headers=_headers(),
        )
        r.raise_for_status()


async def update_record(slug: str, ip: str) -> None:
    record_id = await _get_record_id(slug)
    if not record_id:
        await create_record(slug, ip)
        return
    async with httpx.AsyncClient() as client:
        r = await client.put(
            f"{_CF_BASE}/zones/{settings.cloudflare_zone_id}/dns_records/{record_id}",
            json={"type": "A", "name": f"{slug}.{settings.cloudflare_domain}", "content": ip, "proxied": True},
            headers=_headers(),
        )
        r.raise_for_status()


async def delete_record(slug: str) -> None:
    record_id = await _get_record_id(slug)
    if not record_id:
        return
    async with httpx.AsyncClient() as client:
        r = await client.delete(
            f"{_CF_BASE}/zones/{settings.cloudflare_zone_id}/dns_records/{record_id}",
            headers=_headers(),
        )
        r.raise_for_status()
