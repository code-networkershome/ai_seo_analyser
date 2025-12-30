import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL", "")
key: str = os.getenv("SUPABASE_KEY", "")

# Initialize client only if keys are present to avoid errors during import
# robust handling for when the user hasn't set .env yet
try:
    if url and key:
        supabase: Client = create_client(url, key)
    else:
        supabase = None
        print("Warning: SUPABASE_URL or SUPABASE_KEY not found. Database features will be disabled.")
except Exception as e:
    supabase = None
    print(f"Error initializing Supabase: {e}")

def get_supabase_client() -> Client:
    return supabase
