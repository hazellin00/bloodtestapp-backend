import os
from supabase import create_client, Client

url = "https://fqdyffprucwhftktjynf.supabase.co"
key = "sb_publishable_lGAMWqvn2soPCvdnLK40nA_dkor4amj"
supabase: Client = create_client(url, key)

try:
    with open("database_schema.sql", "r") as f:
        sql = f.read()
    # REST API has no native interface for raw SQL queries unless wrapped in an RPC
    print("REST key cannot execute DDL. Password/Connection String is required to use psql or npx supabase.")
except Exception as e:
    print(f"Error: {e}")
