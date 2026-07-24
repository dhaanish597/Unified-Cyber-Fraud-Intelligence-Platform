# Session Management

Every successful banking login issues a fresh JWT/refresh pair and appends an active session record containing user, device, timestamp, and status. SDK session start creates a unique Fusion session and publishes pipeline updates to authenticated WebSocket subscribers.
