import os

from supabase import Client, create_client
from dotenv import load_dotenv


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

load_dotenv()

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be set. "
        "Copy .env.example to .env and fill in your Supabase project's "
        "Project URL and anon key (Project Settings -> API). "
        "Never use the service_role key here."
    )

# One client, shared by every route that needs Supabase Auth.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
