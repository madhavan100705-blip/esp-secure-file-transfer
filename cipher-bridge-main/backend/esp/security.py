from dataclasses import dataclass
from cryptography.exceptions import InvalidTag
from .encryption import decrypt_file, sha256_hex
from .packet import ESPPacket

@dataclass
class VerificationResult:
    authenticated: bool
    integrity_verified: bool
    recovered: bytes | None


def verify_packet(packet: ESPPacket, associated_data: bytes, tamper: bool = False) -> VerificationResult:
    ciphertext = bytearray(packet.encrypted_payload)
    if tamper and ciphertext:
        ciphertext[0] ^= 0x01
    try:
        recovered = decrypt_file(packet.key, packet.nonce, bytes(ciphertext), packet.authentication_tag, associated_data)
    except InvalidTag:
        return VerificationResult(False, False, None)
    return VerificationResult(True, sha256_hex(recovered) == packet.original_sha256, recovered)
