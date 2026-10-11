
import base64
import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

app = FastAPI(title="ESP Secure File Transfer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory demonstration statistics.
stats = {
    "files_transferred": 0,
    "esp_packets": 0,
    "attacks_detected": 0,
    "packets_rejected": 0,
}

sequence_number = 0


@app.get("/")
def home():
    return {"message": "ESP Secure File Transfer API is running"}


@app.get("/api/health")
def health():
    return {
        "success": True,
        "status": "online",
        "message": "Python backend is ready",
    }


@app.get("/api/status")
def status():
    return {
        "backend": "online",
        "project": "ESP Secure File Transfer",
        "encryption": "AES-256-GCM",
        "mode": "educational simulation",
    }


@app.post("/api/demo")
async def demo(
    file: UploadFile = File(...),
    attack_mode: str = Form("false"),
):
    global sequence_number

    original = await file.read()

    if not original:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(original) > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="For this demonstration, files must be 20 MB or smaller.",
        )

    attack = attack_mode.strip().lower() in ("true", "1", "yes")
    filename = file.filename or "uploaded_file.txt"

    # Sender calculates the original file's SHA-256 digest.
    original_hash = hashlib.sha256(original).hexdigest()

    # Generate a fresh 256-bit AES key and 96-bit nonce.
    # This key is demonstration-only and is not persisted.
    key = AESGCM.generate_key(bit_length=256)
    nonce = secrets.token_bytes(12)
    aes = AESGCM(key)

    # Simulated ESP header information.
    spi = "0x1001"
    sequence_number += 1
    seq = sequence_number

    # Encrypt the file. AESGCM output includes a 16-byte tag.
    encrypted_with_tag = aes.encrypt(nonce, original, None)
    ciphertext = encrypted_with_tag[:-16]
    tag = encrypted_with_tag[-16:]

    # Simulated transmission across an untrusted network.
    transmitted = bytearray(ciphertext)

    if attack and transmitted:
        # Deliberately alter one encrypted byte for the attack demo.
        transmitted[0] ^= 0x01

    stats["esp_packets"] += 1

    try:
        # Receiver authenticates and decrypts the transmitted packet.
        recovered = aes.decrypt(
            nonce,
            bytes(transmitted) + tag,
            None,
        )
        authenticated = True
    except InvalidTag:
        recovered = None
        authenticated = False

    if recovered is not None:
        recovered_hash = hashlib.sha256(recovered).hexdigest()
        integrity_verified = recovered_hash == original_hash
    else:
        integrity_verified = False

    success = authenticated and integrity_verified

    if success:
        stats["files_transferred"] += 1
    else:
        stats["attacks_detected"] += 1
        stats["packets_rejected"] += 1

    # Base64 allows the frontend to reconstruct the recovered file.
    recovered_base64 = (
        base64.b64encode(recovered).decode("ascii")
        if success and recovered is not None
        else None
    )

    # Illustrative ESP-style size: header + nonce + ciphertext + tag.
    header_size = 8
    packet_size = header_size + len(nonce) + len(ciphertext) + len(tag)

    return {
        "success": success,
        "mode": "python_backend",
        "filename": filename,
        "file_size": len(original),
        "sha256": original_hash,
        "spi": spi,
        "sequence": seq,
        "nonce": nonce.hex(),
        "packet_size": packet_size,
        "payload_size": len(ciphertext),
        "authentication_tag": tag.hex(),
        "authenticated": authenticated,
        "authentication_verified": authenticated,
        "integrity_verified": integrity_verified,
        "attack_detected": attack and not authenticated,
        "packet_rejected": not success,
        "encrypted_payload_preview": ciphertext[:32].hex(),
        "recovered_base64": recovered_base64,
        "stats": stats.copy(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
