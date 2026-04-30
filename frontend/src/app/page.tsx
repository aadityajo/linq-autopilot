"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { Play, CheckCircle2, XCircle, Clock, Loader2, ChevronRight } from "lucide-react";

export default function Dashboard() {
  const [runs, setRuns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const fetchRuns = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/runs");
      const data = await res.json();
      setRuns(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns();
    const interval = setInterval(fetchRuns, 3000);
    return () => clearInterval(interval);
  }, []);

  const StatusBadge = ({ status }: { status: string }) => {
    switch (status) {
      case "passed": return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-500/10 text-green-500 border border-green-500/20"><CheckCircle2 className="w-3 h-3" /> Passed</span>;
      case "failed": return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-500/10 text-red-500 border border-red-500/20"><XCircle className="w-3 h-3" /> Failed</span>;
      case "running": return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-500/10 text-blue-500 border border-blue-500/20"><Loader2 className="w-3 h-3 animate-spin" /> Running</span>;
      case "pending": return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-zinc-500/10 text-zinc-400 border border-zinc-500/20"><Clock className="w-3 h-3" /> Pending</span>;
      default: return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-zinc-500/10 text-zinc-400 border border-zinc-500/20">{status}</span>;
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Test Runs</h1>
          <p className="text-muted-foreground mt-1">Monitor and trigger automated scenario tests.</p>
        </div>
        <button onClick={() => setShowModal(true)} className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-all shadow-lg hover:shadow-primary/25">
          <Play className="w-4 h-4 fill-current" /> New Run
        </button>
      </div>

      <div className="glass rounded-xl overflow-hidden">
        <table className="w-full text-sm text-left">
          <thead className="bg-white/5 text-muted-foreground">
            <tr>
              <th className="px-6 py-4 font-medium">Scenario</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 font-medium">Started</th>
              <th className="px-6 py-4 font-medium text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {runs.map((run) => (
              <tr key={run.id} className="hover:bg-white/5 transition-colors group">
                <td className="px-6 py-4 font-medium">{run.scenario_name}</td>
                <td className="px-6 py-4"><StatusBadge status={run.status} /></td>
                <td className="px-6 py-4 text-muted-foreground">
                  {formatDistanceToNow(new Date(run.started_at), { addSuffix: true })}
                </td>
                <td className="px-6 py-4 text-right">
                  <Link href={`/runs/${run.id}`} className="text-primary opacity-0 group-hover:opacity-100 transition-opacity inline-flex items-center gap-1 hover:underline">
                    View Details <ChevronRight className="w-4 h-4" />
                  </Link>
                </td>
              </tr>
            ))}
            {runs.length === 0 && !loading && (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center text-muted-foreground">
                  No runs found. Trigger a new run to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && <NewRunModal onClose={() => setShowModal(false)} />}
    </div>
  );
}

function NewRunModal({ onClose }: { onClose: () => void }) {
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [selected, setSelected] = useState("");
  const [botNumber, setBotNumber] = useState("+16504414144");
  const [callerNumber, setCallerNumber] = useState("+14044267497");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/api/scenarios")
      .then((res) => res.json())
      .then((data) => {
        setScenarios(data.scenarios || []);
        if (data.scenarios?.length > 0) setSelected(data.scenarios[0].filename);
      });
  }, []);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await fetch("http://localhost:8000/api/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario_file: selected, bot_number: botNumber, caller_number: callerNumber }),
      });
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="glass-panel w-full max-w-md rounded-2xl p-6 shadow-2xl animate-in zoom-in-95 duration-200">
        <h2 className="text-xl font-bold mb-4">Trigger New Run</h2>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-1">Scenario</label>
            <select
              className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 outline-none focus:ring-2 focus:ring-primary/50"
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
            >
              {scenarios.map(s => <option key={s.filename} value={s.filename}>{s.name}</option>)}
            </select>
          </div>
          <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">Bot Number <span className="text-xs text-zinc-500">(Linq restaurant line)</span></label>
            <input
              type="text" required
              className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 outline-none focus:ring-2 focus:ring-primary/50"
              value={botNumber} onChange={(e) => setBotNumber(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-1">Caller Number <span className="text-xs text-zinc-500">(simulated user)</span></label>
            <input
              type="text" required placeholder="+1234567890"
              className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 outline-none focus:ring-2 focus:ring-primary/50"
              value={callerNumber} onChange={(e) => setCallerNumber(e.target.value)}
            />
          </div>
          <div className="flex items-center justify-end gap-3 mt-6">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg text-sm font-medium hover:bg-white/10 transition-colors">Cancel</button>
            <button type="submit" disabled={loading} className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2">
              {loading && <Loader2 className="w-4 h-4 animate-spin" />} Start Run
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
