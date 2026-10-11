
import type { TransferResult } from "@/types/simulator";

const API_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

export const checkBackendHealth = async (): Promise<boolean> => {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 2000);

  try {
    const response = await fetch(`${API_URL}/api/health`, {
      method: "GET",
      signal: controller.signal,
    });

    if (!response.ok) {
      return false;
    }

    const data = await response.json();
    return data.success === true && data.status === "online";
  } catch {
    return false;
  } finally {
    window.clearTimeout(timeout);
  }
};

export const runBackendTransfer = async (
  file: File,
  attack: boolean
): Promise<TransferResult> => {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("attack_mode", String(attack));

  const response = await fetch(`${API_URL}/api/demo`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let message = `Transfer failed (HTTP ${response.status}).`;

    try {
      const errorData = await response.json();
      message =
        errorData.detail ||
        errorData.message ||
        message;
    } catch {
      // Keep the HTTP error message if the response isn't JSON.
    }

    throw new Error(message);
  }

  const result = (await response.json()) as TransferResult;

  if (
    typeof result.success !== "boolean" ||
    typeof result.sha256 !== "string" ||
    typeof result.authentication_verified !== "boolean" ||
    typeof result.integrity_verified !== "boolean"
  ) {
    throw new Error("The backend returned an invalid transfer result.");
  }

  // Only a successfully authenticated and verified file may be recovered.
  if (
    result.success &&
    result.authentication_verified &&
    result.integrity_verified &&
    result.recovered_base64
  ) {
    try {
      const binary = window.atob(result.recovered_base64);
      const bytes = new Uint8Array(binary.length);

      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
      }

      result.recovered_bytes = bytes.buffer;
    } catch {
      throw new Error("The recovered file data could not be decoded.");
    }
  } else {
    // Never expose a recovered file after a failed verification.
    result.recovered_bytes = undefined;
  }

  return result;
};
