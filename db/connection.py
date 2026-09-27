from dotenv import load_dotenv
from pathlib import Path
import os
import psycopg

def get_connection():
    # Load .env from config/
    env_path = Path(__file__).resolve().parents[1] / "config" / ".env"
    load_dotenv(env_path)

    db_host = os.getenv("PGHOST", "localhost")
    db_port = os.getenv("PGPORT", "5432")
    db_name = os.getenv("PGDATABASE")
    db_user = os.getenv("PGUSER")
    db_pass = os.getenv("PGPASSWORD")

    if not all([db_name, db_user, db_pass]):
        raise RuntimeError("Database credentials missing from .env")

    conn = psycopg.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_pass
    )

    return conn
