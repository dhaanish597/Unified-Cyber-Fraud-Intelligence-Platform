# Customer Architecture

Customers are persisted in the local SQLite store through the `banking_users` collection. The record contains identity, contact/account fields, registered devices, active sessions, transaction history, location/network history, beneficiaries, security/notification preferences, and risk/trust profile containers. The storage interface is intentionally replaceable by Supabase/Postgres without changing API contracts.
