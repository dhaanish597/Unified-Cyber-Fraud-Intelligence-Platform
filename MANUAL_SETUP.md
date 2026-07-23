# Manual Setup Steps

## GeoLite2 IP Database
1. Create a free account at [MaxMind](https://www.maxmind.com/).
2. Download the `GeoLite2-City` database in MMDB format.
3. Extract the downloaded archive.
4. Place the `GeoLite2-City.mmdb` file in the `data/` directory.

If the file is absent, the system will gracefully fall back to a small hardcoded lookup table for demo purposes.
