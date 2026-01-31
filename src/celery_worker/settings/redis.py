from typing import Optional

from pydantic import BaseModel


class RedisSettings(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    username: Optional[str] = None
    password: Optional[str] = None
    ssl: bool = False

    @property
    def dsn(self) -> str:
        """
        Dynamically builds the Redis DSN (Data Source Name).
        Handles switching between redis:// and rediss:// (SSL).
        """
        scheme = "rediss" if self.ssl else "redis"
        auth = ""

        if self.username or self.password:
            # Handle cases where only password is provided
            u = self.username or ""
            p = self.password or ""
            auth = f"{u}:{p}@"

        return f"{scheme}://{auth}{self.host}:{self.port}/{self.db}"

    @property
    def ssl_options(self) -> dict:
        """
        Returns the SSL context options if SSL is enabled.
        Required for some Celery backend configurations involving cert validation.
        """
        if self.ssl:
            return {"ssl_cert_reqs": "required"}  # Adjust strictly as needed
        return {}
