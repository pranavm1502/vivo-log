"""Entry point for the packaged backend.

This script is used by PyInstaller as the main entry point.
It starts uvicorn serving the FastAPI app.
"""

import os
import sys


def _ensure_database():
    """Create the vivolog database if it doesn't exist."""
    from sqlalchemy import create_engine, text

    sync_url = os.environ.get(
        "VIVOLOG_DATABASE_URL_SYNC",
        "postgresql://postgres:@127.0.0.1:5433/postgres",
    )
    # Connect to the 'postgres' database to create vivolog
    admin_url = sync_url.rsplit("/", 1)[0] + "/postgres"
    try:
        engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'vivolog'")
            )
            if not result.fetchone():
                conn.execute(text("CREATE DATABASE vivolog"))
        engine.dispose()
    except Exception:
        pass  # Database may already exist or connection may fail


def _run_migrations():
    """Run alembic migrations."""
    try:
        from alembic.config import Config
        from alembic import command

        if getattr(sys, '_MEIPASS', None):
            alembic_ini = os.path.join(sys._MEIPASS, 'alembic.ini')
        else:
            alembic_ini = os.path.join(os.path.dirname(__file__), 'alembic.ini')

        if os.path.exists(alembic_ini):
            cfg = Config(alembic_ini)
            if getattr(sys, '_MEIPASS', None):
                cfg.set_main_option('script_location', os.path.join(sys._MEIPASS, 'alembic'))
            # Override the database URL with the sync connection string
            sync_url = os.environ.get(
                "VIVOLOG_DATABASE_URL_SYNC",
                "postgresql://postgres:@127.0.0.1:5433/vivolog",
            )
            cfg.set_main_option('sqlalchemy.url', sync_url)
            command.upgrade(cfg, "head")
    except Exception as e:
        print(f"Migration warning: {e}")


def main():
    # When running from PyInstaller bundle, set the working directory
    # to the bundle directory so alembic.ini and migrations are found.
    if getattr(sys, '_MEIPASS', None):
        os.chdir(sys._MEIPASS)

    _ensure_database()
    _run_migrations()

    import uvicorn

    host = os.environ.get("VIVOLOG_HOST", "127.0.0.1")
    port = int(os.environ.get("VIVOLOG_PORT", "8000"))

    uvicorn.run("app.main:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
