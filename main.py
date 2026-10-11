import base64
import hashlib
import json
import os
import socket
import struct
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ---------------------------------------------------------------------
# ESP-LIKE PACKET
# ---------------------------------------------------------------------

@dataclass
class ESPPacket:
    spi: int
    sequence: int
    nonce: bytes
    ciphertext: bytes
    filename: str

    def serialize(self) -> bytes:
        """Serialize into a compact JSON representation for simulation."""
        obj = {
            "spi": self.spi,
            "sequence": self.sequence,
            "nonce": base64.b64encode(self.nonce).decode(),
            "ciphertext": base64.b64encode(self.ciphertext).decode(),
            "filename": self.filename,
        }
        return json.dumps(obj).encode()

    @staticmethod
    def deserialize(data: bytes):
        obj = json.loads(data.decode())
        return ESPPacket(
            spi=int(obj["spi"]),
            sequence=int(obj["sequence"]),
            nonce=base64.b64decode(obj["nonce"]),
            ciphertext=base64.b64decode(obj["ciphertext"]),
            filename=obj["filename"],
        )


# ---------------------------------------------------------------------
# SECURITY / ESP SIMULATION
# ---------------------------------------------------------------------

class SecureESP:
    def __init__(self):
        # Demo key only. In a real IPsec deployment, keys are negotiated
        # through IKE and are never hard-coded like this.
        self.key = AESGCM.generate_key(bit_length=256)
        self.aes = AESGCM(self.key)
        self.spi = 0x1001
        self.sequence = 0

    def encrypt(self, filename: str, plaintext: bytes) -> ESPPacket:
        self.sequence += 1

        nonce = os.urandom(12)

        # Additional authenticated data binds the packet metadata to the
        # ciphertext. Changing these values causes authentication failure.
        aad = struct.pack("!IQ", self.spi, self.sequence)

        ciphertext = self.aes.encrypt(nonce, plaintext, aad)

        return ESPPacket(
            spi=self.spi,
            sequence=self.sequence,
            nonce=nonce,
            ciphertext=ciphertext,
            filename=filename,
        )

    def decrypt(self, packet: ESPPacket) -> bytes:
        aad = struct.pack("!IQ", packet.spi, packet.sequence)

        # AES-GCM verifies the authentication tag before returning plaintext.
        return self.aes.decrypt(packet.nonce, packet.ciphertext, aad)


# ---------------------------------------------------------------------
# NETWORK / ATTACKER SIMULATION
# ---------------------------------------------------------------------

class NetworkSimulator:
    @staticmethod
    def transmit(packet_bytes: bytes, tamper: bool = False) -> bytes:
        if not tamper:
            return packet_bytes

        obj = json.loads(packet_bytes.decode())
        ciphertext = bytearray(base64.b64decode(obj["ciphertext"]))

        if ciphertext:
            # Flip one bit. This simulates an attacker modifying data
            # while it is in transit.
            ciphertext[len(ciphertext) // 2] ^= 0x01

        obj["ciphertext"] = base64.b64encode(bytes(ciphertext)).decode()
        return json.dumps(obj).encode()


# ---------------------------------------------------------------------
# OPTIONAL SOCKET SIMULATION
# ---------------------------------------------------------------------

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ---------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP Secure File Transfer Simulation")
        self.root.geometry("900x680")
        self.root.minsize(820, 620)

        self.esp = SecureESP()
        self.selected_file = None

        self.file_var = tk.StringVar(value="No file selected")
        self.tamper_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready")
        self.seq_var = tk.StringVar(value="0")
        self.packet_size_var = tk.StringVar(value="-")
        self.hash_original_var = tk.StringVar(value="-")
        self.hash_received_var = tk.StringVar(value="-")

        self.build_ui()

    def build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        header = ttk.Frame(self.root, padding=18)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="ESP SECURE FILE TRANSFER",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Software-only IPsec ESP simulation: confidentiality + integrity",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        branch = ttk.Frame(self.root, padding=(18, 4))
        branch.pack(fill="x")

        self.branch_box(branch, "BRANCH OFFICE A\nSENDER", 0)
        ttk.Label(
            branch, text="  →  INTERNET / ATTACKER  →  ",
            font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=1, padx=15)
        self.branch_box(branch, "BRANCH OFFICE B\nRECEIVER", 2)

        file_frame = ttk.LabelFrame(
            self.root, text="1. Select Confidential File", padding=15
        )
        file_frame.pack(fill="x", padx=18, pady=12)

        ttk.Label(file_frame, textvariable=self.file_var).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(
            file_frame, text="Choose File", command=self.choose_file
        ).pack(side="right")

        settings = ttk.LabelFrame(
            self.root, text="2. Transmission Settings", padding=15
        )
        settings.pack(fill="x", padx=18, pady=6)

        ttk.Label(settings, text="Encryption:").grid(row=0, column=0, sticky="w")
        ttk.Label(
            settings, text="AES-256-GCM",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=1, sticky="w", padx=8)

        ttk.Label(settings, text="ESP SPI:").grid(row=0, column=2, sticky="w", padx=(35, 0))
        ttk.Label(
            settings, text="0x1001",
            font=("Consolas", 10, "bold")
        ).grid(row=0, column=3, sticky="w", padx=8)

        ttk.Checkbutton(
            settings,
            text="Simulate attacker tampering with packet",
            variable=self.tamper_var
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(12, 0))

        actions = ttk.Frame(self.root, padding=(18, 10))
        actions.pack(fill="x")

        ttk.Button(
            actions, text="SEND FILE",
            command=self.send_file
        ).pack(side="left", ipadx=18, ipady=7)

        ttk.Button(
            actions, text="Create Sample File",
            command=self.create_sample
        ).pack(side="left", padx=10, ipadx=8, ipady=7)

        ttk.Button(
            actions, text="Clear Log",
            command=self.clear_log
        ).pack(side="right", ipadx=8, ipady=7)

        stats = ttk.LabelFrame(
            self.root, text="3. Security / Transmission Results", padding=12
        )
        stats.pack(fill="x", padx=18, pady=4)

        labels = [
            ("Sequence Number", self.seq_var),
            ("ESP Packet Size", self.packet_size_var),
            ("Original SHA-256", self.hash_original_var),
            ("Received SHA-256", self.hash_received_var),
        ]

        for i, (name, var) in enumerate(labels):
            ttk.Label(stats, text=name + ":").grid(
                row=i // 2, column=(i % 2) * 2, sticky="w", padx=5, pady=3
            )
            ttk.Label(
                stats, textvariable=var, font=("Consolas", 9)
            ).grid(
                row=i // 2, column=(i % 2) * 2 + 1,
                sticky="w", padx=5, pady=3
            )

        log_frame = ttk.LabelFrame(
            self.root, text="4. Simulation Log", padding=8
        )
        log_frame.pack(fill="both", expand=True, padx=18, pady=(8, 18))

        self.log = tk.Text(
            log_frame, height=14, wrap="word",
            font=("Consolas", 10), state="disabled"
        )
        self.log.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            log_frame, orient="vertical", command=self.log.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.log.configure(yscrollcommand=scrollbar.set)

        self.write_log("System initialized.")
        self.write_log(f"Simulated sender IP: {get_local_ip()}")
        self.write_log("ESP security association ready.")
        self.write_log("Select a file and press SEND FILE.")

    def branch_box(self, parent, text, column):
        box = ttk.Frame(parent, relief="solid", borderwidth=1, padding=14)
        box.grid(row=0, column=column)
        ttk.Label(
            box, text=text, justify="center",
            font=("Segoe UI", 10, "bold")
        ).pack()

    def write_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="Select confidential file"
        )
        if path:
            self.selected_file = path
            self.file_var.set(path)
            self.write_log(f"Selected file: {path}")

    def create_sample(self):
        path = Path(tempfile.gettempdir()) / "confidential_project_report.txt"
        content = (
            "CONFIDENTIAL PROJECT REPORT\n"
            "Branch Office A -> Branch Office B\n"
            "This file is used to demonstrate ESP encryption and integrity.\n"
            "If an attacker changes the encrypted packet, authentication fails.\n"
        )
        path.write_text(content, encoding="utf-8")
        self.selected_file = str(path)
        self.file_var.set(str(path))
        self.write_log(f"Sample confidential file created: {path}")

    def send_file(self):
        if not self.selected_file:
            messagebox.showwarning(
                "No file",
                "Choose a file or create the sample file first."
            )
            return

        try:
            threading.Thread(
                target=self._send_worker, daemon=True
            ).start()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _send_worker(self):
        try:
            self.status_var.set("Transmitting...")

            path = Path(self.selected_file)
            plaintext = path.read_bytes()

            original_hash = hashlib.sha256(plaintext).hexdigest()
            self.root.after(
                0, lambda: self.hash_original_var.set(original_hash)
            )

            self.root.after(
                0, lambda: self.write_log(
                    f"[SENDER] Read {len(plaintext)} bytes from {path.name}"
                )
            )

            packet = self.esp.encrypt(path.name, plaintext)
            raw_packet = packet.serialize()

            self.root.after(
                0, lambda: self.seq_var.set(str(packet.sequence))
            )
            self.root.after(
                0, lambda: self.packet_size_var.set(
                    f"{len(raw_packet)} bytes"
                )
            )

            self.root.after(
                0, lambda: self.write_log(
                    "[ESP] File encrypted with AES-256-GCM."
                )
            )
            self.root.after(
                0, lambda: self.write_log(
                    f"[ESP] SPI=0x{packet.spi:X}, Sequence={packet.sequence}"
                )
            )
            self.root.after(
                0, lambda: self.write_log(
                    "[ESP] Authentication tag generated."
                )
            )

            tampered = self.tamper_var.get()

            self.root.after(
                0, lambda: self.write_log(
                    "[NETWORK] Encrypted ESP packet sent over simulated Internet."
                )
            )

            if tampered:
                self.root.after(
                    0, lambda: self.write_log(
                        "[ATTACKER] Packet intercepted and modified!"
                    )
                )
            else:
                self.root.after(
                    0, lambda: self.write_log(
                        "[ATTACKER] Can see packet bytes but cannot read plaintext."
                    )
                )

            received_raw = NetworkSimulator.transmit(
                raw_packet, tamper=tampered
            )
            received_packet = ESPPacket.deserialize(received_raw)

            self.root.after(
                0, lambda: self.write_log(
                    "[RECEIVER] ESP packet received."
                )
            )

            try:
                received_plaintext = self.esp.decrypt(received_packet)
            except Exception:
                self.root.after(
                    0, lambda: self.write_log(
                        "[RECEIVER] ✗ INTEGRITY VERIFICATION FAILED"
                    )
                )
                self.root.after(
                    0, lambda: self.write_log(
                        "[RECEIVER] Packet rejected. File was not accepted."
                    )
                )
                self.root.after(
                    0, lambda: self.status_var.set("TAMPER DETECTED")
                )
                return

            received_hash = hashlib.sha256(received_plaintext).hexdigest()
            self.root.after(
                0, lambda: self.hash_received_var.set(received_hash)
            )

            if received_hash != original_hash:
                self.root.after(
                    0, lambda: self.write_log(
                        "[RECEIVER] ✗ HASH MISMATCH"
                    )
                )
                self.root.after(
                    0, lambda: self.status_var.set("INTEGRITY ERROR")
                )
                return

            output_dir = Path(__file__).parent / "received_files"
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / received_packet.filename
            output_file.write_bytes(received_plaintext)

            self.root.after(
                0, lambda: self.write_log(
                    "[RECEIVER] ✓ Authentication verified."
                )
            )
            self.root.after(
                0, lambda: self.write_log(
                    "[RECEIVER] ✓ File decrypted successfully."
                )
            )
            self.root.after(
                0, lambda: self.write_log(
                    f"[RECEIVER] ✓ SHA-256 matches."
                )
            )
            self.root.after(
                0, lambda: self.write_log(
                    f"[RECEIVER] File saved: {output_file}"
                )
            )
            self.root.after(
                0, lambda: self.status_var.set("TRANSFER SUCCESSFUL")
            )

        except Exception as exc:
            self.root.after(
                0, lambda: self.write_log(f"[ERROR] {exc}")
            )
            self.root.after(
                0, lambda: self.status_var.set("ERROR")
            )


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
