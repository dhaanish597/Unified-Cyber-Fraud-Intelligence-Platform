# Manual Setup Steps

## GeoLite2 IP Database
1. Create a free account at [MaxMind](https://www.maxmind.com/).
2. Download the `GeoLite2-City` database in MMDB format.
3. Extract the downloaded archive.
4. Place the `GeoLite2-City.mmdb` file in the `data/` directory.

If the file is absent, the system will gracefully fall back to a small hardcoded lookup table for demo purposes.

## Payment Gateway Webhook
1. Create an account on Razorpay or Cashfree (Sandbox mode).
2. Generate a webhook secret.
3. Add `GATEWAY_WEBHOOK_SECRET=your_secret` to your `.env` file.
4. Point the webhook URL to your server (`POST /gateway/webhook`).
