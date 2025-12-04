#!/usr/bin/env python3
# scripts/log_2fa_cron.py
import os
from datetime import datetime, timezone
from app.totp_utils import generate_totp_code

SEED_PATH = "/data/seed.txt"   # persistent volume inside container

def read_seed():
    try:
        with open(SEED_PATH, "r") as f:
            return f.read().strip()
    except Exception:
        return None

def main():
    seed = read_seed()
    if not seed:
        print("No seed found")
        return
    try:
        code = generate_totp_code(seed)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"{ts} - 2FA Code: {code}")
    except Exception as e:
        print("Error generating code:", e)

if __name__ == "__main__":
    main()
