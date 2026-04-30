"use client";

import { useEffect, useState } from "react";
import { Beaker, FileText, ListOrdered } from "lucide-react";

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState<any[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/scenarios")
      .then(res => res.json())
      .then(data => setScenarios(data.scenarios || []));
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Beaker className="w-8 h-8 text-primary" /> Scenario Library
        </h1>
        <p className="text-muted-foreground mt-2 text-lg">Browse available test scenarios loaded from YAML.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {scenarios.map((s) => (
          <div key={s.filename} className="glass rounded-xl p-6 hover:-translate-y-1 transition-transform cursor-default group">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-xl group-hover:text-primary transition-colors">{s.name}</h3>
              <span className="text-xs font-mono bg-white/10 px-2 py-1 rounded text-muted-foreground flex items-center gap-1">
                <FileText className="w-3 h-3"/> {s.filename}
              </span>
            </div>
            <p className="text-muted-foreground text-sm mb-6 leading-relaxed min-h-[40px]">{s.description}</p>
            
            <div className="border-t border-white/5 pt-4 flex items-center gap-2 text-sm font-medium">
              <ListOrdered className="w-4 h-4 text-primary" /> {s.step_count} Steps
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
