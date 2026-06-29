import React from 'react';
import { ShieldAlert, Flame, Zap } from 'lucide-react';

export default function RescuePlanCard({ plan }) {
  if (!plan) return null;

  const steps = plan
    .split(/\n+/)
    .map(step => step.replace(/^\d+\.\s*/, '').trim())
    .filter(step => step.length > 0);

  return (
    <div className="card-elevated border-l-4 border-l-red-400 overflow-hidden">
      <div className="bg-red-50 px-5 py-3 flex items-center justify-between border-b border-red-100">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-red-500" />
          <span className="text-xs font-semibold text-red-600">
            Atlas Recovery Strategy Activated
          </span>
        </div>
        <div className="flex items-center gap-1 bg-red-100 text-red-600 text-[10px] px-2 py-0.5 rounded-lg font-semibold">
          <Flame className="w-3 h-3" /> Critical
        </div>
      </div>

      <div className="p-5">
        <div className="flex gap-3 items-start">
          <div className="p-2 rounded-xl bg-red-50 text-red-500 shrink-0">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground text-sm">
              Timeline Deficit Detected
            </h3>
            <p className="text-xs text-muted-foreground leading-relaxed mt-1">
              Atlas has prepared a recovery strategy. Following this sequence maximizes your completion probability.
            </p>
          </div>
        </div>

        <div className="mt-4 space-y-2">
          {steps.map((step, index) => (
            <div key={index} className="flex gap-3 items-start bg-[#FAFBFC] border border-border rounded-xl p-3 hover:border-red-200 transition-all duration-200">
              <span className="flex items-center justify-center font-semibold text-[10px] bg-red-50 text-red-500 w-5 h-5 rounded-lg shrink-0">
                {index + 1}
              </span>
              <p className="text-xs text-foreground font-medium leading-relaxed">
                {step}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
