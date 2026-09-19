from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    registry_api_key: str
    cloudflare_api_token: str
    cloudflare_zone_id: str
    cloudflare_domain: str = "near2far.family"
    db_path: str = "registry.db"
    port: int = 5102

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
