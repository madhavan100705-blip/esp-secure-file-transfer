import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

type MetricCardProps = {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone?: "cyan" | "green" | "red" | "amber";
};

const tones = {
  cyan: "text-cyan-300 border-cyan-400/20 bg-cyan-400/[0.06]",
  green: "text-emerald-300 border-emerald-400/20 bg-emerald-400/[0.06]",
  red: "text-rose-300 border-rose-400/20 bg-rose-400/[0.06]",
  amber: "text-amber-300 border-amber-400/20 bg-amber-400/[0.06]",
};

export function MetricCard({ label, value, icon: Icon, tone = "cyan" }: MetricCardProps) {
  return (
    <motion.div layout className={`rounded-2xl border p-4 shadow-[0_18px_50px_rgba(2,8,23,0.18)] ${tones[tone]}`}>
      <div className="flex items-center justify-between gap-3">
        <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">{label}</span>
        <Icon className="h-4 w-4 opacity-80" />
      </div>
      <motion.div key={String(value)} initial={{ opacity: 0.4, y: 6 }} animate={{ opacity: 1, y: 0 }} className="mt-3 font-mono text-2xl font-semibold tracking-tight text-slate-100">
        {value}
      </motion.div>
    </motion.div>
  );
}
