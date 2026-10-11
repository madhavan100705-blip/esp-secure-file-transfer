# ESP Secure File Transfer Simulation

A software-only Python simulation of an IPsec ESP-style secure file transfer between two branch offices.

Features:
- AES-256-GCM authenticated encryption
- ESP-like packet structure with SPI, sequence number, nonce, ciphertext and authentication tag
- Sender and receiver simulation
- Network/attacker simulation
- Tamper detection
- Simple Tkinter GUI
- No physical hardware required

## Run

```bash
python -m pip install -r requirements.txt
python main.py
```

Python 3.10+ recommended.

## Demonstration

1. Choose a file or create a sample file.
2. Click "Send File".
3. The application encrypts the file and creates an ESP-like packet.
4. The packet is transmitted through the simulated Internet.
5. The receiver verifies the authentication tag and decrypts the file.
6. Enable "Tamper packet" and send again. The receiver should reject it.

This is an educational ESP/IPsec simulation, not a replacement for a production IPsec implementation.
