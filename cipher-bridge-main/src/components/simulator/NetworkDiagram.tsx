import { AnimatePresence, motion } from "framer-motion";
import { Eye, Globe2, Laptop, ShieldCheck } from "lucide-react";
import type { TransferStage } from "@/types/simulator";

type Props = { stage: TransferStage; attack: boolean; presentation?: boolean };

const nodes = [
  { key: "sender", label: "Branch office A", sub: "Sender", icon: Laptop },
  { key: "gateway-a", label: "ESP gateway", sub: "Encrypting", icon: ShieldCheck },
  { key: "internet", label: "Internet", sub: "Untrusted network", icon: Globe2 },
  { key: "attacker", label: "Network monitor", sub: "Observing traffic", icon: Eye },
  { key: "gateway-b", label: "ESP gateway", sub: "Verifying", icon: ShieldCheck },
  { key: "receiver", label: "Branch office B", sub: "Receiver", icon: Laptop },
];

const activeFor = (key: string, stage: TransferStage) => {
  if (key === "sender") return ["file_selected", "hashing", "encrypting", "packet_created"].includes(stage);
  if (key === "gateway-a") return ["encrypting", "packet_created"].includes(stage);
  if (key === "internet") return ["transmitting", "intercepted"].includes(stage);
  if (key === "attacker") return stage === "intercepted";
  if (key === "gateway-b") return ["received", "authenticating", "integrity_check", "decrypting", "success", "attack_detected"].includes(stage);
  return ["received", "authenticating", "integrity_check", "decrypting", "success"].includes(stage);
};

export function NetworkDiagram({ stage, attack, presentation = false }: Props) {
  const packetVisible = !["idle", "file_selected", "hashing", "encrypting"].includes(stage);
  const danger = attack && ["intercepted", "attack_detected"].includes(stage);
  return (
    <div className={`relative overflow-hidden rounded-3xl border border-cyan-300/10 bg-[#071323] ${presentation ? "min-h-[420px]" : "min-h-[295px]"}`}>
      <div className="absolute inset-0 opacity-70 [background-image:linear-gradient(rgba(34,211,238,.045)_1px,transparent_1px),linear-gradient(90deg,rgba(34,211,238,.045)_1px,transparent_1px)] [background-size:42px_42px]" />
      <div className="absolute -right-16 -top-16 h-44 w-44 rounded-full bg-cyan-400/10 blur-3xl" />
      <div className="relative flex h-full min-h-[295px] flex-col justify-center gap-5 px-4 py-8 md:flex-row md:items-center md:gap-0 md:px-8">
        {nodes.map((node, index) => {
          const Icon = node.icon;
          const active = activeFor(node.key, stage);
          const isAttacker = node.key === "attacker";
          return (
            <div key={node.key} className="flex flex-1 items-center md:h-28 md:flex-col md:justify-center">
              <motion.div animate={{ scale: active ? 1.04 : 1 }} className={`relative z-10 flex w-full max-w-[160px] items-center gap-3 rounded-2xl border px-3 py-3 transition-colors md:flex-col md:gap-2 md:px-2 ${danger && isAttacker ? "border-rose-400/60 bg-rose-400/10 text-rose-100 shadow-[0_0_28px_rgba(251,113,133,.18)]" : active ? "border-cyan-300/45 bg-cyan-300/10 text-cyan-50 shadow-[0_0_26px_rgba(34,211,238,.14)]" : "border-white/10 bg-slate-950/50 text-slate-400"}`}>
                <div className={`rounded-xl p-2 ${danger && isAttacker ? "bg-rose-400/20" : active ? "bg-cyan-300/15" : "bg-white/[0.05]"}`}><Icon className="h-5 w-5" /></div>
                <div className="min-w-0 text-left md:text-center"><p className="truncate text-[11px] font-semibold uppercase tracking-[0.1em]">{node.label}</p><p className="mt-1 truncate text-[10px] text-slate-500">{danger && isAttacker ? "Payload modified" : node.sub}</p></div>
                {active && <motion.span animate={{ opacity: [0.35, 1, 0.35] }} transition={{ repeat: Infinity, duration: 1.6 }} className={`absolute -right-1 -top-1 h-2.5 w-2.5 rounded-full ${danger && isAttacker ? "bg-rose-400" : "bg-cyan-300"}`} />}
              </motion.div>
              {index < nodes.length - 1 && <div className="relative mx-2 h-px flex-1 bg-white/10 md:mx-0 md:h-px md:w-full"><motion.div animate={{ opacity: active ? 1 : 0.4 }} className={`absolute inset-y-0 left-0 w-full ${danger && index === 2 ? "bg-rose-400" : "bg-cyan-300"} shadow-[0_0_12px_currentColor]`} /></div>}
            </div>
          );
        })}
        <AnimatePresence>
          {packetVisible && <motion.div initial={{ opacity: 0, x: "-20%" }} animate={{ opacity: 1, x: ["0%", "720%"] }} transition={{ duration: 2.2, ease: "easeInOut" }} className={`pointer-events-none absolute left-[12%] top-1/2 z-20 hidden h-3 w-3 rounded-full md:block ${danger ? "bg-rose-400 shadow-[0_0_18px_#fb7185]" : stage === "success" ? "bg-emerald-400 shadow-[0_0_18px_#34d399]" : "bg-cyan-300 shadow-[0_0_18px_#22d3ee]"}`} />}
        </AnimatePresence>
      </div>
      <div className="absolute bottom-3 left-4 flex items-center gap-2 text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-500"><span className="h-1.5 w-1.5 rounded-full bg-cyan-300" /> Secure path visualization <span className="text-slate-700">/</span> <span className="font-mono normal-case tracking-normal text-slate-400">{stage.replace(/_/g, " ")}</span></div>
    </div>
  );
}
