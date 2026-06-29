import React from 'react';
import { Calendar, CheckCircle, Clock, TrendingUp } from 'lucide-react';

export default function TaskCard({ task, isSelected, onClick, onDelete }) {
  const completedMissions = task.missions ? task.missions.filter(m => m.is_completed).length : 0;
  const totalMissions = task.missions ? task.missions.length : 0;
  const progress = totalMissions > 0 ? Math.round((completedMissions / totalMissions) * 100) : 0;

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div
      onClick={onClick}
      className={`w-full p-4.5 rounded-2xl border cursor-pointer flex flex-col justify-between gap-3 text-left group transition-all duration-350 ${
        isSelected
          ? 'border-primary/35 bg-primary/[0.03] shadow-[0_4px_16px_rgba(99,102,241,0.06)] ring-1 ring-primary/10'
          : 'border-border bg-white hover:bg-slate-50/50 hover:shadow-[0_4px_20px_rgba(0,0,0,0.015)] hover:-translate-y-0.5'
      }`}
    >
      <div className="flex justify-between items-start gap-2.5">
        <div className="truncate flex-1">
          <h4 className="font-bold text-sm text-foreground truncate group-hover:text-primary transition-colors duration-200">
            {task.title}
          </h4>
          <span className="text-[10px] font-medium text-muted-foreground flex items-center gap-1.5 mt-1.5">
            <Clock className="w-3.5 h-3.5 text-muted-foreground/60" /> Due {formatDate(task.deadline)}
          </span>
        </div>

        {task.status === 'completed' ? (
          <span className="bg-emerald-50 text-emerald-600 border border-emerald-100 text-[10px] font-bold px-2 py-0.5 rounded-lg flex items-center gap-1 shrink-0">
            <CheckCircle className="w-3 h-3" /> Done
          </span>
        ) : (
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-lg border flex items-center gap-1 shrink-0 ${
              task.risk_level === 'High'
                ? 'bg-red-50 text-red-600 border-red-100'
                : task.risk_level === 'Medium'
                ? 'bg-amber-50 text-amber-600 border-amber-100'
                : 'bg-emerald-50 text-emerald-600 border-emerald-100'
            }`}
          >
            {task.risk_level}
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div className="w-full pt-1.5 border-t border-slate-100/50">
        <div className="flex justify-between items-center text-[10px] text-muted-foreground mb-1.5 font-medium">
          <span>{completedMissions} of {totalMissions} milestones</span>
          <span className="font-semibold text-foreground">{progress}%</span>
        </div>
        <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 progress-animated ${
              task.status === 'completed' ? 'bg-emerald-500' : 'bg-primary'
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
}
