# Notification Service

`api/platform/notifications.py` records security notifications in SQLite and exposes `/banking/notifications` to the authenticated customer. New-device logins create an in-app notification and publish a WebSocket `security_notification` envelope. Email delivery remains an adapter boundary for a configured Supabase Auth or free SMTP provider; no paid service is required.
