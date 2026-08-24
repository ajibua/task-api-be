import os
from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

# Falls back to a local SQLite file if DATABASE_URL isn't set, so the app
# still runs without Docker/Postgres for quick local checks. In normal use,
# DATABASE_URL comes from .env and points at Postgres.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tasks.db")

engine = create_engine(DATABASE_URL, echo=False)
