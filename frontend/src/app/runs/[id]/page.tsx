"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { CheckCircle2, XCircle, Loader2, ArrowLeft, Clock, Smartphone, MessageSquare } from "lucide-react";
import Link from "next/link";

export default function RunDetail() {
  const params = useParams();
  const id = params.id as string;
  const [data, setData] = useState<any>(null);

  const fetchDetails = async () => {
    const res = await fetch(`http://localhost:8000/api/runs/${id}`);
    const json = await res.json();
    setData(json);
  };

  useEffect(() => {
    fetchDetails();
    
    const interval = setInterval(async () => {
      const res = await fetch(`http://localhost:8000/api/runs/${id}`);
      const json = await res.json();
      setData(json);
      if (["passed", "failed", "timeout"].includes(json.run?.status)) {
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [id]);

  if (!data) return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;

  const run = data.run;
  const steps = data.steps || [];

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <Link href="/" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-2">
        <ArrowLeft className="w-4 h-4" /> Back to Runs
      </Link>
      
      <div className="glass rounded-xl p-6 border-l-4" style={{ borderLeftColor: run.status === 'passed' ? '#22c55e' : run.status === 'failed' ? '#ef4444' : '#3b82f6' }}>
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">{run.scenario_name}</h1>
          <span className="uppercase tracking-wider text-xs font-bold px-3 py-1 rounded-full bg-white/10">
            {run.status}
          </span>
        </div>
        <div className="flex items-center gap-6 text-sm text-muted-foreground">
          <div className="flex items-center gap-2"><Smartphone className="w-4 h-4"/> Bot: {run.to_number}</div>
          <div className="flex items-center gap-2"><Clock className="w-4 h-4"/> Started: {new Date(run.started_at).toLocaleTimeString()}</div>
        </div>
      </div>

      <div className="space-y-6 mt-8">
        <h2 className="text-xl font-semibold flex items-center gap-2"><MessageSquare className="w-5 h-5"/> Timeline</h2>
        
        {steps.map((step: any, i: number) => (
          <div key={step.id} className="glass rounded-xl p-6 space-y-6">
            <div className="flex items-center justify-between text-xs text-muted-foreground uppercase tracking-widest font-bold">
              <span>Step {i + 1}</span>
              {step.linq_trace_id && <span className="font-mono bg-black/30 px-2 py-1 rounded">Trace: {step.linq_trace_id}</span>}
            </div>
            
            <div className="space-y-4">
              <div className="bubble-sent">
                {step.message_sent}
              </div>
              
              {step.status === "running" ? (
                <div className="flex items-center gap-2 text-sm text-muted-foreground ml-4">
                  <Loader2 className="w-4 h-4 animate-spin" /> Waiting for bot...
                </div>
              ) : step.response_received ? (
                <div className="bubble-received">
                  {step.response_received}
                </div>
              ) : (
                <div className="text-sm text-red-400 italic ml-4">No response received</div>
              )}
            </div>

            {(step.assertions_passed?.length > 0 || step.assertions_failed?.length > 0 || step.failure_reasons?.length > 0) && (
              <div className="bg-black/20 rounded-lg p-4 text-sm mt-4">
                <div className="flex items-center gap-4 mb-2 text-muted-foreground text-xs font-semibold uppercase">
                  <span>Latency: {step.response_latency_ms || 0}ms</span>
                  {step.protocol_used && <span>Protocol: {step.protocol_used}</span>}
                </div>
                <ul className="space-y-2 mt-3 border-t border-white/5 pt-3">
                  {step.assertions_passed?.map((a: string, idx: number) => (
                    <li key={`pass-${idx}`} className="flex items-start gap-2 text-green-400">
                      <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" /> <span className="opacity-90">Assertion passed: {a}</span>
                    </li>
                  ))}
                  {step.failure_reasons?.map((f: string, idx: number) => (
                    <li key={`fail-${idx}`} className="flex items-start gap-2 text-red-400">
                      <XCircle className="w-4 h-4 mt-0.5 shrink-0" /> <span className="opacity-90">{f}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
