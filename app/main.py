from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from .crypto_utils import decrypt_seed
from .totp_utils import generate_totp_code, verify_totp_code

app = FastAPI()   # ⬅️ this is what uvicorn is expecting

DATA_FILE = "data/seed.txt"

class SeedRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

# POST /decrypt-seed
@app.post("/decrypt-seed")
def decrypt_endpoint(payload: SeedRequest):
    try:
        # load private key
        with open("student_private.pem", "rb") as f:
            private_key = crypto_utils.load_private_key(f.read())

        seed = decrypt_seed(payload.encrypted_seed, private_key)

        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w") as f:
            f.write(seed)

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Decryption failed")

# GET /generate-2fa
@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(DATA_FILE, "r") as f:
        seed = f.read().strip()

    code = generate_totp_code(seed)
    import time
    valid_for = 30 - (int(time.time()) % 30)
    return {"code": code, "valid_for": valid_for}

# POST /verify-2fa
@app.post("/verify-2fa")
def verify_2fa(payload: VerifyRequest):
    if not payload.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(DATA_FILE, "r") as f:
        seed = f.read().strip()

    valid = verify_totp_code(seed, payload.code)
    return {"valid": valid}
