import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
bucket_name = os.environ.get("SUPABASE_BUCKET")

supabase = create_client(supabase_url, supabase_key)