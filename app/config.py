import os


def _normalize_database_url(url: str) -> str:
    """Ajusta o prefixo da URL do Neon.tech para o driver psycopg3 do SQLAlchemy."""
    if not url:
        raise RuntimeError(
            "A variável DATABASE_URL não está definida. "
            "Configure-a no arquivo .env (local) ou nas Environment Variables do Render.com."
        )
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "nutci-3gre-dev-secret-key")
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.getenv("DATABASE_URL", ""))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Otimização de pool para PostgreSQL Serverless (Neon.tech) no Render.com
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": 5,
        "max_overflow": 10,
    }
