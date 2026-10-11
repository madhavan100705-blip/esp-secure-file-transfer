import { ChevronDown, ChevronUp, Code2, Fingerprint, Hash, KeyRound, Radio, ShieldCheck } from "lucide-react";
import { useState } from "react";
import type { TransferResult } from "@/types/simulator";

type Props = { packet: TransferResult | null };

export function PacketInspector({ packet }: Props) {
  const [expanded, setExpanded] = useState(false);
  const display = packet || { spi: "0x1001", sequence: 0, nonce: "••••••••••••••••", authentication_tag: "••••••••••••••••", payload_size: 0, packet_size: 0, encrypted_payload_preview: "Awaiting encrypted payload" };
  const fields = [
    { label: "SPI", value: display.spi, icon: Radio },
    { label: "Sequence number", value: display.sequence ? String(display.sequence).padStart(6, "0") : "000000", icon: Hash },
    { label: "Nonce / IV", value: display.nonce.slice(0, 22), icon: KeyRound },
    { label: "Authentication tag", value: display.authentication_tag.slice(0, 22), icon: Fingerprint },
  ];
  return (
    <div className="rounded-2xl border border-white/10 bg-[#0a1729] p-5">
      <div className="flex items-start justify-between gap-4"><div><div className="flex items-center gap-2 text-cyan-300"><Code2 className="h-4 w-4" /><span className="text-[10px] font-semibold uppercase tracking-[0.18em]">ESP packet inspector</span></div><h3 className="mt-2 font-mono text-sm text-slate-200">ESP PACKET #{String(display.sequence || 1).padStart(6, "0")}</h3></div><span className={`rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-wider ${packet?.success === false ? "border-rose-400/30 bg-rose-400/10 text-rose-300" : packet ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-300" : "border-slate-500/30 bg-slate-500/10 text-slate-400"}`}>{packet?.success === false ? "Rejected" : packet ? "Authenticated" : "Standby"}</span></div>
      <div className="mt-5 grid grid-cols-2 gap-2 xl:grid-cols-4">{fields.map(({ label, value, icon: Icon }) => <div key={label} className="rounded-xl border border-white/[0.07] bg-slate-950/40 p-3"><Icon className="h-3.5 w-3.5 text-slate-500" /><p className="mt-3 text-[9px] uppercase tracking-[0.13em] text-slate-500">{label}</p><p className="mt-1 truncate font-mono text-[10px] text-slate-200">{value}</p></div>)}</div>
      <div className="mt-2 grid grid-cols-2 gap-2"><div className="rounded-xl border border-white/[0.07] bg-slate-950/40 p-3"><p className="text-[9px] uppercase tracking-[0.13em] text-slate-500">Encrypted payload</p><p className="mt-1 font-mono text-[10px] text-cyan-200">{display.payload_size || "—"} B</p></div><div className="rounded-xl border border-white/[0.07] bg-slate-950/40 p-3"><p className="text-[9px] uppercase tracking-[0.13em] text-slate-500">Packet size</p><p className="mt-1 font-mono text-[10px] text-cyan-200">{display.packet_size || "—"} B</p></div></div>
      {expanded && <div className="mt-3 rounded-xl border border-cyan-300/10 bg-[#07101e] p-3"><div className="grid grid-cols-4 overflow-hidden rounded-lg border border-white/10 text-[9px] font-semibold uppercase tracking-wider text-slate-500"><div className="border-r border-white/10 p-2">SPI</div><div className="border-r border-white/10 p-2">Sequence</div><div className="border-r border-white/10 p-2">Nonce</div><div className="p-2">Payload</div><div className="border-r border-t border-white/10 p-2 font-mono text-cyan-200">{display.spi}</div><div className="border-r border-t border-white/10 p-2 font-mono text-cyan-200">{String(display.sequence || 0).padStart(6, "0")}</div><div className="border-r border-t border-white/10 p-2 font-mono text-slate-300">{display.nonce.slice(0, 10)}…</div><div className="border-t border-white/10 p-2 font-mono text-slate-300">{display.encrypted_payload_preview || "ENCRYPTED"}…</div></div><p className="mt-3 break-all font-mono text-[10px] leading-relaxed text-slate-500">{display.encrypted_payload_preview || "No payload has been generated. Start a transfer to inspect authenticated ciphertext."}</p></div>}
      <button onClick={() => setExpanded((value) => !value)} className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 py-2.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-300 transition hover:border-cyan-300/30 hover:text-cyan-200">{expanded ? "Hide packet bytes" : "View packet"}{expanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}</button>
      <div className="mt-3 flex items-center gap-2 text-[10px] text-slate-500"><ShieldCheck className="h-3.5 w-3.5 text-emerald-400" /> Authenticated encryption protects the payload and metadata.</div>
    </div>
  );
}
