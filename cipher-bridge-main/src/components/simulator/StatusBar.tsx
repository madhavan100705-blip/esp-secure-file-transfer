import { Activity, CheckCircle2, LockKeyhole, ShieldCheck } from "lucide-react";

type StatusBarProps = { backendOnline: boolean };

export function StatusBar({ backendOnline }: StatusBarProps) {
  const items = [
    { label: "System status", value: "Operational", icon: Activity, tone: "text-emerald-300" },
    { label: "Security mode", value: "ESP simulation", icon: ShieldCheck, tone: "text-cyan-300" },
    { label: "Encryption", value: "AES-256-GCM", icon: LockKeyhole, tone: "text-cyan-300" },
    { label: "Integrity", value: "Authenticated", icon: CheckCircle2, tone: "text-emerald-300" },
  ];
  return (
    <div className="border-y border-white/[0.07] bg-slate-950/50">
      <div className="mx-auto grid max-w-[1440px] grid-cols-2 divide-x divide-white/[0.06] px-5 py-2.5 lg:grid-cols-5 lg:px-8">
        {items.map(({ label, value, icon: Icon, tone }) => (
          <div key={label} className="flex items-center gap-2 px-3 py-1 first:pl-0 lg:px-5">
            <Icon className={`h-3.5 w-3.5 ${tone}`} />
            <div className="min-w-0">
              <p className="truncate text-[9px] font-semibold uppercase tracking-[0.17em] text-slate-500">{label}</p>
              <p className={`truncate font-mono text-[10px] uppercase tracking-wider ${tone}`}>{value}</p>
            </div>
          </div>
        ))}
        <div className="col-span-2 flex items-center gap-2 border-t border-white/[0.06] px-3 pt-2 lg:col-span-1 lg:border-t-0 lg:px-5 lg:pt-1">
          <span className={`h-2 w-2 rounded-full ${backendOnline ? "bg-emerald-400 shadow-[0_0_10px_#34d399]" : "bg-cyan-400 shadow-[0_0_10px_#22d3ee]"}`} />
          <div><p className="text-[9px] font-semibold uppercase tracking-[0.17em] text-slate-500">Backend</p><p className="font-mono text-[10px] uppercase tracking-wider text-slate-300">{backendOnline ? "Python / online" : "Browser / local"}</p></div>
        </div>
      </div>
    </div>
  );
}
