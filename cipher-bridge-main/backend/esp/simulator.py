from .encryption import encrypt_file
from .packet import ESPPacket
from .security import verify_packet

class TransferSimulator:
    def __init__(self) -> None:
        self.sequence = 0
        self.spi = "0x1001"
        self.stats = {"files_transferred": 0, "esp_packets": 0, "attacks_detected": 0, "packets_rejected": 0}

    def transfer(self, filename: str, data: bytes, attack: bool = False) -> dict:
        self.sequence += 1
        associated_data = f"{self.spi}:{self.sequence}:{filename}".encode()
        encrypted = encrypt_file(data, associated_data)
        packet = ESPPacket(self.spi, self.sequence, encrypted.nonce, encrypted.ciphertext, encrypted.tag, encrypted.sha256, encrypted.key)
        self.stats["esp_packets"] += 1
        verification = verify_packet(packet, associated_data, tamper=attack)
        if verification.authenticated and verification.integrity_verified:
            self.stats["files_transferred"] += 1
        else:
            self.stats["attacks_detected"] += 1
            self.stats["packets_rejected"] += 1
        return {
            "success": verification.authenticated and verification.integrity_verified,
            "mode": "python_backend",
            "filename": filename,
            "file_size": len(data),
            "sha256": encrypted.sha256,
            "spi": packet.spi,
            "sequence": packet.sequence,
            "nonce": packet.nonce.hex(),
            "packet_size": packet.packet_size,
            "payload_size": len(packet.encrypted_payload),
            "authentication_tag": packet.authentication_tag.hex(),
            "authenticated": verification.authenticated,
            "authentication_verified": verification.authenticated,
            "integrity_verified": verification.integrity_verified,
            "attack_detected": attack and not verification.authenticated,
            "packet_rejected": not verification.authenticated,
            "recovered_hex": verification.recovered.hex() if verification.recovered else None,
            "encrypted_payload_preview": packet.encrypted_payload.hex()[:72],
            "stats": self.stats.copy(),
        }
