import { FileText, UploadCloud, X } from "lucide-react";
import { useRef, useState } from "react";

type Props = { file: File | null; hash: string; onFile: (file: File) => void; onClear: () => void };

export function FileUploader({ file, hash, onFile, onClear }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const selectFile = (candidate?: File) => {
    if (candidate && candidate.size <= 25 * 1024 * 1024) onFile(candidate);
  };
  return (
    <div>
      {!file ? (
        <div onDragOver={(event) => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={(event) => { event.preventDefault(); setDragging(false); selectFile(event.dataTransfer.files[0]); }} onClick={() => inputRef.current?.click()} role="button" tabIndex={0} onKeyDown={(event) => { if (event.key === "Enter") inputRef.current?.click(); }} className={`group cursor-pointer rounded-2xl border border-dashed p-7 text-center transition ${dragging ? "border-cyan-300 bg-cyan-300/10" : "border-white/15 bg-white/[0.025] hover:border-cyan-300/40 hover:bg-cyan-300/[0.04]"}`}>
          <input ref={inputRef} type="file" className="hidden" onChange={(event) => selectFile(event.target.files?.[0])} />
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-300/20 bg-cyan-300/10 text-cyan-300 transition group-hover:scale-105"><UploadCloud className="h-5 w-5" /></div>
          <p className="mt-4 text-sm font-semibold text-slate-200">{dragging ? "Release to upload" : "Drop confidential file"}</p>
          <p className="mt-1 text-xs text-slate-500">Drag & drop your file here or choose a file</p>
          <span className="mt-4 inline-flex rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-300">Choose file</span>
          <p className="mt-3 font-mono text-[9px] text-slate-600">MAX 25 MB · ALL COMMON FILE TYPES</p>
        </div>
      ) : (
        <div className="rounded-2xl border border-emerald-300/20 bg-emerald-300/[0.05] p-4">
          <div className="flex items-start justify-between gap-3"><div className="flex min-w-0 items-center gap-3"><div className="rounded-xl bg-emerald-300/10 p-2 text-emerald-300"><FileText className="h-5 w-5" /></div><div className="min-w-0"><p className="truncate text-sm font-semibold text-slate-100">{file.name}</p><p className="mt-1 font-mono text-[10px] uppercase text-slate-500">{file.type || "Binary file"} · {(file.size / 1024).toFixed(1)} KB</p></div></div><button onClick={onClear} aria-label="Remove selected file" className="rounded-lg p-1.5 text-slate-500 transition hover:bg-white/10 hover:text-slate-200"><X className="h-4 w-4" /></button></div>
          <div className="mt-4 border-t border-white/10 pt-3"><p className="text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-500">SHA-256 fingerprint</p><p className="mt-1 break-all font-mono text-[10px] leading-relaxed text-emerald-200/80">{hash || "Calculating…"}</p></div>
          <div className="mt-3 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-emerald-300"><span className="h-1.5 w-1.5 rounded-full bg-emerald-300" /> Ready for encryption</div>
        </div>
      )}
    </div>
  );
}
