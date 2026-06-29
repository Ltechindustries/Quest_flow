import React from 'react';
import { Sparkles, ShieldAlert, Award, TrendingUp } from 'lucide-react';

export default function RiskIndicator({ priorityScore, riskScore, completionProbability, reason }) {
  const probPercentage = completionProbability <= 1.0 ? Math.round(completionProbability * 100) : Math.round(completionProbability);
  
  const getPrioritySub = (val) => {
    if (val > 75) return "High Impact";
    if (val > 40) return "Medium Impact";
    return "Standard";
  };

  const getRiskSub = (val) => {
    if (val > 70) return "At Risk";
    if (val > 30) return "Moderate Risk";
    return "Stable Timeline";
  };

  const getProbSub = (val) => {
    if (val > 75) return "Highly Viable";
    if (val > 40) return "Viable";
    return "Timeline Deficit";
  };

  const renderMetric = (val, label, subtext, color, borderHoverColor, icon) => (
    <div className={`flex flex-col justify-between bg-white border border-slate-100 rounded-2xl p-4.5 flex-1 transition-all duration-300 hover:border-${borderHoverColor} hover:shadow-[0_4px_20px_rgba(0,0,0,0.015)]`}>
      <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
        {icon} {label}
      </span>
      <div className="my-2.5">
        <span className={`text-3xl font-extrabold tracking-tight ${color}`}>
          {Math.round(val)}{label === 'Completion' ? '%' : ''}
        </span>
      </div>
      <span className="text-[10px] font-semibold text-muted-foreground/80 mt-0.5">
        {subtext}
      </span>
    </div>
  );

  return (
    <div className="card-elevated p-6 flex flex-col gap-5">
      <h3 className="text-[13px] font-semibold text-foreground flex items-center gap-2">
        <TrendingUp className="w-4 h-4 text-primary" /> Atlas Assessment
      </h3>

      <div className="flex flex-col sm:flex-row gap-4 w-full">
        {renderMetric(priorityScore, 'Priority', getPrioritySub(priorityScore), 'text-violet-600', 'violet-200', <Sparkles className="w-3.5 h-3.5 text-violet-500" />)}
        {renderMetric(riskScore, 'Risk', getRiskSub(riskScore), 'text-amber-600', 'amber-200', <ShieldAlert className="w-3.5 h-3.5 text-amber-500" />)}
        {renderMetric(probPercentage, 'Completion', getProbSub(probPercentage), 'text-emerald-600', 'emerald-200', <Award className="w-3.5 h-3.5 text-emerald-500" />)}
      </div>

      {reason && (
        <div className="p-4 bg-slate-50/50 border border-slate-100 rounded-xl text-xs leading-relaxed text-muted-foreground">
          <span className="text-primary font-bold mr-1">Atlas Assessment:</span>
          {reason}
        </div>
      )}
    </div>
  );
}
