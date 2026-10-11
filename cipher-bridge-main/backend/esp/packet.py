from dataclasses import dataclass

@dataclass
class ESPPacket:
    spi: str
    sequence: int
    nonce: bytes
    encrypted_payload: bytes
    authentication_tag: bytes
    original_sha256: str
    key: bytes

    @property
    def packet_size(self) -> int:
        return 4 + 4 + len(self.nonce) + len(self.encrypted_payload) + len(self.authentication_tag)

    def as_metadata(self) -> dict:
        return {
            "spi": self.spi,
            "sequence": self.sequence,
            "nonce": self.nonce.hex(),
            "encrypted_payload": self.encrypted_payload.hex(),
            "authentication_tag": self.authentication_tag.hex(),
            "payload_size": len(self.encrypted_payload),
            "packet_size": self.packet_size,
        }
