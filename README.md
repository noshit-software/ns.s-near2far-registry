# ns.s-near2far-registry

Slug registration API for near2far.family. Creates and manages `{slug}.near2far.family` DNS records via Cloudflare. Runs on Robert's VPS — family servers never touch it directly after install.

## Stack

- FastAPI + aiosqlite (SQLite)
- Docker Compose
- Cloudflare DNS API

## Quickstart

```bash
cp .env.example .env   # fill in values
docker compose up --build
```

API: http://localhost:5102/health

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | none | DB connectivity check |
| GET | `/api/check/{slug}` | none | Check slug availability |
| POST | `/api/register` | API key | Register a slug, create DNS record |
| POST | `/api/update` | token | Update IP for existing slug |
| DELETE | `/api/delete` | API key | Remove a slug and its DNS record |

### Register

```
POST /api/register
Authorization: Bearer <REGISTRY_API_KEY>
{ "slug": "smiths", "ip": "1.2.3.4" }

→ { "success": true, "data": { "slug": "smiths", "token": "<update-token>" } }
```

The `token` is required for future IP updates. Store it — it's not recoverable.

### Update IP (dynamic DNS)

```
POST /api/update
{ "slug": "smiths", "ip": "1.2.3.5", "token": "<update-token>" }
```

## Slug rules

- 3–30 characters, lowercase alphanumeric + hyphens
- No leading or trailing hyphens
- Reserved: `www`, `api`, `registry`, `gps`, `mail`, `near2far`, `gardunia`, `admin`, `help`, `support`, `status`

## nginx config (VPS)

```nginx
server {
    listen 80;
    server_name registry.near2far.family;

    location / {
        proxy_pass http://127.0.0.1:5102;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```
