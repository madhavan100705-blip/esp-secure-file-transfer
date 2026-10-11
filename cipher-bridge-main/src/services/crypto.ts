import type { TransferResult } from "@/types/simulator";

const encoder = new TextEncoder();

export const bytesToHex = (bytes: Uint8Array) =>
  Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");

export const hexToBytes = (hex: string) => {
  const bytes = new Uint8Array(hex.length / 2);
  for (let index = 0; index < bytes.length; index += 1) {
    bytes[index] = Number.parseInt(hex.slice(index * 2, index * 2 + 2), 16);
  }
  return bytes;
};

export const sha256Hex = async (data: ArrayBuffer) =>
  bytesToHex(new Uint8Array(await crypto.subtle.digest("SHA-256", data)));

export const runBrowserTransfer = async (
  file: File,
  attack: boolean,
  sequence: number,
): Promise<TransferResult> => {
  const bytes = await file.arrayBuffer();
  const originalHash = await sha256Hex(bytes);
  const spi = "0x1001";
  const associatedData = encoder.encode(`${spi}:${sequence}:${file.name}`);
  const key = await crypto.subtle.generateKey({ name: "AES-GCM", length: 256 }, true, ["encrypt", "decrypt"]);
  const nonce = crypto.getRandomValues(new Uint8Array(12));
  const encryptedWithTag = new Uint8Array(
    await crypto.subtle.encrypt({ name: "AES-GCM", iv: nonce, tagLength: 128, additionalData: associatedData }, key, bytes),
  );
  const tag = encryptedWithTag.slice(-16);
  const ciphertext = encryptedWithTag.slice(0, -16);
  const transmitted = new Uint8Array(ciphertext);
  if (attack && transmitted.length > 0) transmitted[0] ^= 1;

  let recoveredBytes: ArrayBuffer | undefined;
  let authenticated = false;
  if (!attack) {
    try {
      recoveredBytes = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv: nonce, tagLength: 128, additionalData: associatedData },
        key,
        new Uint8Array([...transmitted, ...tag]),
      );
      authenticated = true;
    } catch {
      authenticated = false;
    }
  }
  const recoveredHash = recoveredBytes ? await sha256Hex(recoveredBytes) : "";
  const integrityVerified = authenticated && recoveredHash === originalHash;
  return {
    success: authenticated && integrityVerified,
    mode: "browser_simulation",
    filename: file.name,
    file_size: file.size,
    sha256: originalHash,
    spi,
    sequence,
    nonce: bytesToHex(nonce),
    packet_size: 4 + 4 + nonce.length + ciphertext.length + tag.length,
    payload_size: ciphertext.length,
    authentication_tag: bytesToHex(tag),
    authenticated,
    authentication_verified: authenticated,
    integrity_verified: integrityVerified,
    attack_detected: attack && !authenticated,
    packet_rejected: !authenticated,
    encrypted_payload_preview: bytesToHex(ciphertext).slice(0, 72),
    recovered_bytes: recoveredBytes,
  };
};
