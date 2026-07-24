# Supabase Integration

The current executable reference uses SQLite and PBKDF2/JWT so the demo runs without paid infrastructure. Supabase is an optional free deployment adapter: map `banking_users` to `auth.users` plus a customer profile table, validate Supabase JWT claims in `PlatformSecurityMiddleware`, and retain the existing endpoint/pipeline contracts. No Supabase credentials are fabricated in development.
