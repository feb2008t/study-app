from supabase import create_client

SUPABASE_URL = "https://emjbpmjgnspbjoomecsj.supabase.co"
SUPABASE_KEY = "sb_publishable_XReVlpVCAbTvGsli5Ak7qQ_VPCM4FEO"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)