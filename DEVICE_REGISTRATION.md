# Device Registration

Developer Portal pairing creates a five-minute bootstrap record. The APK exchanges the one-time token at `/device/register`, receives device credentials, stores runtime configuration in encrypted preferences, then uses the normal authenticated SDK registration/session path. Device records are marked `LIVE_DEVICE`; synthetic records remain separate.
