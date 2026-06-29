import React, { useState } from 'react';
import { Lock, CheckCircle2, Circle, Swords, Loader2 } from 'lucide-react';

export default function MissionChain({ missions = [], onCompleteMission }) {
  const [loadingMissionId, setLoadingMissionId] = useState(null);

  const handleComplete = async (missionId) => {
    setLoadingMissionId(missionId);
    try {
      await onCompleteMission(missionId);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingMissionId(null);
    }
  };

  const sortedMissions = [...missions].sort((a, b) => a.order_index - b.order_index);

  return (
    <div className="glass-panel rounded-xl p-6 relative overflow-hidden">
      {/* Decorative light beam */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

      <h2 className="text-xl font-bold flex items-center gap-2 mb-6 text-foreground">
        <Swords className="w-5 h-5 text-primary" /> Active Questline
      </h2>

      <div className="relative pl-6 border-l-2 border-border/80 space-y-6">
        {sortedMissions.map((mission, idx) => {
          const isCompleted = mission.is_completed;
          const isUnlocked = mission.is_unlocked;
          const isActive = isUnlocked && !isCompleted;
          const isLocked = !isUnlocked && !isCompleted;

          return (
            <div key={mission.id} className="relative group">
              {/* Timeline Connector Indicator Node */}
              <div className="absolute -left-[31px] top-1.5 flex items-center justify-center">
                {isCompleted ? (
                  <div className="w-4 h-4 rounded-full bg-emerald-500 border-4 border-background flex items-center justify-center shadow-lg shadow-emerald-500/20" />
                ) : isActive ? (
                  <div className="w-4 h-4 rounded-full bg-primary border-4 border-background flex items-center justify-center animate-ping absolute" />
                ) : null}
                
                {/* Secondary static dot for active to keep layout clean */}
                {isActive && (
                  <div className="w-4 h-4 rounded-full bg-primary border-4 border-background flex items-center justify-center shadow-lg shadow-primary/30" />
                )}
                
                {isLocked && (
                  <div className="w-4 h-4 rounded-full bg-[#18181b] border-2 border-border flex items-center justify-center" />
                )}
              </div>

              {/* Mission Content Panel */}
              <div
                className={`transition-all duration-300 rounded-lg p-4 border ${
                  isCompleted
                    ? 'border-emerald-950/20 bg-emerald-950/5 opacity-60'
                    : isActive
                    ? 'border-primary/30 bg-primary/5 glow-rose shadow-md'
                    : 'border-white/5 bg-transparent opacity-40 select-none'
                }`}
              >
                <div className="flex justify-between items-center gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-mono tracking-widest text-muted-foreground uppercase">
                        Mission {mission.order_index}
                      </span>
                      {isActive && (
                        <span className="text-[9px] font-semibold bg-primary/20 text-primary px-1.5 py-0.5 rounded tracking-wider uppercase animate-pulse">
                          Active
                        </span>
                      )}
                    </div>
                    <h3
                      className={`text-sm font-semibold transition-all ${
                        isCompleted
                          ? 'line-through text-muted-foreground'
                          : 'text-foreground'
                      }`}
                    >
                      {mission.title}
                    </h3>
                  </div>

                  {/* Interactive Buttons */}
                  <div>
                    {isCompleted ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                    ) : isActive ? (
                      <button
                        onClick={() => handleComplete(mission.id)}
                        disabled={loadingMissionId !== null}
                        className="bg-primary/10 hover:bg-primary text-primary hover:text-white border border-primary/20 hover:border-transparent text-xs font-semibold py-1.5 px-3 rounded-md transition-all flex items-center gap-1 active:scale-95 disabled:opacity-50"
                      >
                        {loadingMissionId === mission.id ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <>Complete</>
                        )}
                      </button>
                    ) : (
                      <Lock className="w-4 h-4 text-muted-foreground shrink-0" />
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
