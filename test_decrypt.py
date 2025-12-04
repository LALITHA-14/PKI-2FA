from app.crypto_utils import decrypt_seed

with open("encrypted_seed.txt") as f:
    encrypted = f.read().strip()

print(decrypt_seed(encrypted))