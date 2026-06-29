import React, { useState } from 'react';
import { Lock, CheckCircle2, Loader2 } from 'lucide-react';

export default function MissionCard({ mission, onComplete }) {
  const [loading, setLoading] = useState(false);

  const isCompleted = mission.is_completed;
  const isUnlocked = mission.is_unlocked;
  const isActive = isUnlocked && !isCompleted;
  const isLocked = !isUnlocked && !isCompleted;

  const handleCompleteClick = async () => {
    if (!onComplete || loading) return;
    setLoading(true);
    try {
      await onComplete(mission.id);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className={`transition-all duration-300 rounded-2xl p-4 border flex items-center justify-between gap-4 mission-unlock-enter ${
        isCompleted
          ? 'border-emerald-200 bg-emerald-50/50'
          : isActive
          ? 'border-primary/25 bg-primary/[0.03] shadow-card hover:shadow-card-hover'
          : 'border-border bg-[#FAFBFC] opacity-60 select-none'
      }`}
    >
      <div className="flex items-center gap-3.5 flex-1 min-w-0">
        {/* Order Indicator */}
        <div
          className={`h-8 w-8 rounded-xl font-semibold text-xs flex items-center justify-center shrink-0 ${
            isCompleted
              ? 'bg-emerald-100 text-emerald-600'
              : isActive
              ? 'bg-primary/10 text-primary'
              : 'bg-secondary text-muted-foreground'
          }`}
        >
          {mission.order_index}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5 mb-0.5">
            <span className="text-[10px] text-muted-foreground">
              Milestone
            </span>
            {isActive && (
              <span className="text-[9px] font-semibold bg-primary/10 text-primary px-1.5 py-0.5 rounded-md">
                Active
              </span>
            )}
          </div>
          <h4
            className={`text-sm font-medium truncate transition-all ${
              isCompleted ? 'line-through text-muted-foreground' : 'text-foreground'
            }`}
          >
            {mission.title}
          </h4>
        </div>
      </div>

      <div>
        {isCompleted ? (
          <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
        ) : isActive ? (
          <button
            onClick={handleCompleteClick}
            disabled={loading}
            className="bg-primary hover:bg-primary-light text-white text-xs font-semibold py-1.5 px-4 rounded-xl transition-all flex items-center gap-1.5 active:scale-95 disabled:opacity-50 shadow-sm hover:shadow-md focus-ring"
          >
            {loading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <>Complete</>
            )}
          </button>
        ) : (
          <div className="p-1.5 rounded-lg bg-secondary text-muted-foreground">
            <Lock className="w-3.5 h-3.5" />
          </div>
        )}
      </div>
    </div>
  );
}
