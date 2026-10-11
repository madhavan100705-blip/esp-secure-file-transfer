from dataclasses import dataclass
import hashlib
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

@dataclass
class EncryptedPayload:
    key: bytes
    nonce: bytes
    ciphertext: bytes
    tag: bytes
    sha256: str

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def encrypt_file(data: bytes, associated_data: bytes) -> EncryptedPayload:
    key = AESGCM.generate_key(bit_length=256)
    nonce = secrets.token_bytes(12)
    encrypted = AESGCM(key).encrypt(nonce, data, associated_data)
    return EncryptedPayload(key, nonce, encrypted[:-16], encrypted[-16:], sha256_hex(data))

def decrypt_file(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes, associated_data: bytes) -> bytes:
    return AESGCM(key).decrypt(nonce, ciphertext + tag, associated_data)
