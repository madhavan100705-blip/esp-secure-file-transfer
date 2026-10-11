# CipherBridge — ESP Secure File Transfer Simulator

**Secure. Verify. Transfer.**

CipherBridge is a premium educational simulation of secure file transfer between two branch offices. It demonstrates IPsec Encapsulating Security Payload concepts, AES-256-GCM authenticated encryption, SHA-256 integrity verification, SPI and sequence metadata, packet inspection, tamper detection, and the conceptual role of replay protection.

> **Educational ESP/IPsec Simulation** — This project demonstrates the concepts of IPsec Encapsulating Security Payload through a software simulation. It is not intended to replace a production IPsec implementation.

## Features

- Real AES-256-GCM encryption and authentication in the Python service.
- Browser fallback using the Web Crypto API when FastAPI is unavailable.
- ESP-style packets with SPI, sequence number, nonce, encrypted payload, and authentication tag.
- Animated normal transfer and attack/tampering demonstrations.
- Download of the recovered original file only after authentication and SHA-256 verification.
- Persistent local browser statistics and activity timeline for demonstrations.
- Packet Inspector, Network Monitor, Attack Lab, About/Viva content, and projector-friendly Presentation Mode.

## Security concept

The simulator reads a file, computes SHA-256, encrypts it with AES-256-GCM, and wraps the encrypted bytes in a simulated ESP packet. AES-GCM produces an authentication tag. If the encrypted payload changes in transit, tag verification fails and decryption is blocked. The original and recovered data are then compared with SHA-256.

## Architecture

`Branch Office A → ESP Security Gateway → Untrusted Internet / Monitor → ESP Security Gateway → Branch Office B`

The browser uses `GET /api/health` to detect the optional FastAPI service. When it responds, transfer requests use Python backend mode. Otherwise, the same flow runs locally using Web Crypto.

## Technology stack

- React, TypeScript, Vite, Tailwind CSS, shadcn/ui, Framer Motion, Lucide React
- Python, FastAPI, cryptography, python-multipart
- No database; backend state is in memory and browser history uses localStorage

## Project structure

- `src/pages/Index.tsx` — simulator experience and state machine
- `src/components/simulator/` — visual network, packet, uploader, and status components
- `src/services/crypto.ts` — browser Web Crypto implementation
- `src/services/api.ts` — backend health and transfer client
- `backend/esp/` — encryption, packet, and verification primitives
- `backend/main.py` — FastAPI API

## Installation

Install frontend dependencies with the project package manager, then install the Python dependencies from `backend/requirements.txt` in a Python 3.11+ environment.

## Frontend setup

Copy `.env.example` to `.env` when the FastAPI service is running on a non-default URL. Start the Vite development server through the project tooling.

## Backend setup

From the repository root, run the FastAPI app with Uvicorn using `backend.main:app` on port 8000. The backend allows the local Vite origins used by the simulator.

## Running locally

Open the Vite URL in a browser. With FastAPI unavailable, the status bar reports **BROWSER SIMULATION MODE**. With FastAPI running, it reports **PYTHON BACKEND ONLINE**.

## Browser simulation mode

Browser mode uses `crypto.subtle.digest`, `crypto.subtle.generateKey`, `crypto.subtle.encrypt`, and `crypto.subtle.decrypt` with AES-GCM. The key is generated in memory and never sent to the backend.

## Python backend mode

FastAPI performs AES-256-GCM, SHA-256, packet creation, tampering, authentication, decryption, and recovered data generation in memory. It exposes `/api/health`, `/api/status`, `/api/encrypt`, `/api/transmit`, `/api/receive`, `/api/attack`, `/api/reset`, and `/api/demo`.

## Normal transfer demo

Choose **Start demo** or upload a file and select **Encrypt & send**. The pipeline progresses through file selection, hashing, encryption, packet creation, transmission, authentication, decryption, and integrity verification.

## Attack demo

Choose **Attack demo** or enable Attack Lab mode. The simulated monitor flips a byte in the ciphertext before the receiver verifies the AES-GCM tag. Authentication fails, decryption is blocked, and no download is offered.

## Presentation mode

Presentation Mode hides dense controls and presents the branch-to-branch network flow, state explanation, and two large demo actions for a projector.

## API documentation

FastAPI exposes interactive API documentation at `/docs` when the backend is running. Uploads use multipart form data. `/api/demo` accepts `file` and `attack_mode`.

## Security limitations

This is an educational ESP/IPsec-inspired simulation. It does not create real IPsec packets, establish tunnel or transport mode, negotiate keys, manage Security Associations, implement a kernel packet path, or provide a production replay window. Sequence values illustrate the concept only. Do not use it as a VPN or as a replacement for a reviewed IPsec implementation.

## Viva questions and answers

- **What is ESP?** Encapsulating Security Payload is an IPsec protocol concept that can provide confidentiality, integrity, and origin authentication for protected traffic.
- **Why is encryption required?** It prevents an observer on an untrusted network from directly reading the file contents.
- **What is AES-GCM?** An authenticated encryption mode that encrypts data and produces a tag for tamper detection.
- **What is confidentiality?** Keeping protected information unreadable to unauthorized observers.
- **What is integrity?** Confidence that protected data was not changed in transit.
- **What is authentication?** Verification that the protected ciphertext and associated metadata are valid and unmodified.
- **What is an authentication tag?** A cryptographic value checked by GCM before plaintext is released.
- **What is SPI?** A Security Parameters Index used conceptually to identify the security association for a packet.
- **What is a sequence number?** A monotonically increasing packet value used as an input to replay protection mechanisms.
- **What is replay protection?** Rejecting an old valid packet that is sent again; this UI demonstrates the concept, not a complete replay window.
- **How does the attacker simulation work?** It flips a bit in the encrypted payload before the receiver verifies the tag.
- **How is tampering detected?** AES-GCM tag verification fails for the modified ciphertext.
- **Why does AES-GCM reject modified ciphertext?** The authentication tag no longer matches the ciphertext and associated data.
- **Is this a real IPsec VPN?** No. It is an educational software simulation.
- **What is the difference between simulation and production IPsec?** Production IPsec involves negotiated security associations, kernel/network integration, key lifecycle, policy, replay windows, and operational controls not represented here.
