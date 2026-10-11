
export type TransferStage =
  | "idle"
  | "file_selected"
  | "hashing"
  | "encrypting"
  | "packet_created"
  | "transmitting"
  | "intercepted"
  | "received"
  | "authenticating"
  | "integrity_check"
  | "decrypting"
  | "success"
  | "attack_detected";

export type TransferResult = {
  success: boolean;
  mode: "python_backend" | "browser_simulation";

  filename: string;
  file_size: number;
  sha256: string;

  spi: string;
  sequence: number;
  nonce: string;
  packet_size: number;
  payload_size: number;
  authentication_tag: string;
  encrypted_payload_preview: string;

  authenticated: boolean;
  authentication_verified: boolean;
  integrity_verified: boolean;
  attack_detected: boolean;
  packet_rejected: boolean;

  // Recovered file data returned by the Python backend.
  recovered_base64?: string | null;

  // Decoded file bytes for the existing frontend download flow.
  recovered_bytes?: ArrayBuffer;
  recovered_hex?: string | null;

  stats?: {
    files_transferred: number;
    esp_packets: number;
    attacks_detected: number;
    packets_rejected: number;
  };
};

export type ActivityEvent = {
  id: string;
  time: string;
  title: string;
  detail: string;
  tone: "cyan" | "green" | "amber" | "red" | "slate";
};

export type SessionStats = {
  filesTransferred: number;
  espPackets: number;
  attacksDetected: number;
  successfulTransfers: number;
  packetsRejected: number;
};
