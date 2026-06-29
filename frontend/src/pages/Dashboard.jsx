import React, { useState, useEffect } from 'react';
import MissionCard from '../components/MissionCard';
import RiskIndicator from '../components/RiskIndicator';
import RescuePanel from '../components/RescuePanel';
import { 
  Trash2, 
  RefreshCw, 
  Compass, 
  Swords, 
  EyeOff, 
  Calendar, 
  Layers,
  Award,
  Sparkles,
  Clock,
  Target,
  Brain,
  Zap,
  ChevronDown,
  ChevronUp,
  History,
  AlertTriangle,
  Play,
  X
} from 'lucide-react';

export default function Dashboard({ task, onCompleteMission, onReanalyze, onDeleteTask }) {
  const [reanalyzing, setReanalyzing] = useState(false);
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const [isSimulationOpen, setIsSimulationOpen] = useState(false);
  const [simulatedDeadline, setSimulatedDeadline] = useState('');
  const [simulatedMissions, setSimulatedMissions] = useState([]);
  const [availableHours, setAvailableHours] = useState(8);
  const [simulationResult, setSimulationResult] = useState(null);
  const [simulating, setSimulating] = useState(false);
  const [simError, setSimError] = useState('');

  const handleOpenSimulation = () => {
    if (!task) return;
    let formattedDate = '';
    if (task.deadline) {
      const dateObj = new Date(task.deadline);
      const year = dateObj.getFullYear();
      const month = String(dateObj.getMonth() + 1).padStart(2, '0');
      const day = String(dateObj.getDate()).padStart(2, '0');
      formattedDate = `${year}-${month}-${day}`;
    }
    setSimulatedDeadline(formattedDate);
    setSimulatedMissions(task.missions.filter(m => m.is_completed).map(m => m.id));
    setAvailableHours(8);
    setSimulationResult(null);
    setSimError('');
    setIsSimulationOpen(true);
  };

  const handleRunSimulation = async () => {
    if (!simulatedDeadline) {
      setSimError("Deadline is required for simulation.");
      return;
    }
    setSimulating(true);
    setSimError('');
    try {
      const res = await fetch(`/api/tasks/${task.id}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          simulated_deadline: simulatedDeadline,
          completed_mission_ids: simulatedMissions,
          available_hours_per_day: availableHours
        })
      });
      if (!res.ok) throw new Error(await res.text() || "Failed to run simulation");
      const data = await res.json();
      setSimulationResult(data);
    } catch (err) {
      console.error(err);
      setSimError(err.message || "An unexpected error occurred during simulation.");
    } finally {
      setSimulating(false);
    }
  };

  useEffect(() => {
    if (!task?.id) return;
    
    let isMounted = true;
    const fetchTimeline = async () => {
      try {
        const res = await fetch(`/api/tasks/${task.id}/timeline`);
        if (!res.ok) throw new Error("Failed to fetch timeline");
        const data = await res.json();
        if (isMounted) {
          setTimelineEvents(data);
        }
      } catch (err) {
        console.error("Error loading timeline:", err);
      }
    };
    
    fetchTimeline();
    return () => {
      isMounted = false;
    };
  }, [task?.id, task?.priority_score, task?.risk_score, task?.completion_probability]);

  if (!task) return null;

  const sortedMissions = [...task.missions].sort((a, b) => a.order_index - b.order_index);
  const activeMission = sortedMissions.find(m => m.is_unlocked && !m.is_completed);
  const previewMissions = sortedMissions.filter(m => m.id !== activeMission?.id);
  const completedCount = sortedMissions.filter(m => m.is_completed).length;
  const progressPct = sortedMissions.length > 0 ? Math.round((completedCount / sortedMissions.length) * 100) : 0;

  const handleForceReanalyze = async () => {
    if (reanalyzing) return;
    setReanalyzing(true);
    try {
      await onReanalyze(task.id);
    } catch (err) {
      console.error(err);
    } finally {
      setReanalyzing(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-6">
      
      {/* Atlas Briefing — Visual Hero */}
      {task.daily_brief && (
        <div className="card-elevated p-8 relative overflow-hidden bg-gradient-to-br from-indigo-50/40 via-white to-violet-50/30 border border-indigo-100/30 shadow-[0_8px_32px_rgba(99,102,241,0.02)]">
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-bold tracking-wider text-primary flex items-center gap-1.5 bg-primary/10 px-3 py-1 rounded-lg">
                <Sparkles className="w-3.5 h-3.5" /> Atlas Briefing
              </span>
              {task.status !== 'completed' && (
                <span className="text-[10px] font-bold text-muted-foreground bg-secondary px-2.5 py-1 rounded-lg">
                  Active Strategy
                </span>
              )}
            </div>
            
            <h3 className="text-xl md:text-2xl font-extrabold text-foreground leading-tight tracking-tight">
              {task.daily_brief.headline}
            </h3>
            
            <p className="text-sm md:text-base text-muted-foreground/90 leading-relaxed font-medium">
              {task.daily_brief.summary}
            </p>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 mt-2 pt-4 border-t border-slate-100 text-sm">
              <div className="space-y-1">
                <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider block">Today's Focus</span>
                <span className="text-foreground font-semibold text-sm">{task.daily_brief.today_focus}</span>
              </div>
              {task.daily_brief.warning && (
                <div className="space-y-1">
                  <span className="text-[10px] uppercase font-bold text-red-500 tracking-wider block">Warning Flag</span>
                  <span className="text-red-600 font-semibold text-sm">{task.daily_brief.warning}</span>
                </div>
              )}
            </div>
            
            <div className="mt-2 pl-4 border-l-2 border-primary/20 text-xs italic text-primary/80 leading-relaxed">
              “{task.daily_brief.motivation}”
            </div>
          </div>
        </div>
      )}

      {/* Task Info Header */}
      <div className="card-elevated p-6 relative overflow-hidden bg-white">
        <div className="absolute top-4 right-4 flex items-center gap-2">
          <button
            onClick={handleOpenSimulation}
            className="flex items-center gap-1.5 px-3 py-2 bg-primary hover:bg-primary-light text-white text-xs font-semibold rounded-xl transition-all duration-200 active:scale-95 shadow-sm hover:shadow-[0_4px_12px_rgba(99,102,241,0.2)] focus-ring"
            title="Simulate Plan"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Simulate</span>
          </button>
          <button
            onClick={handleForceReanalyze}
            disabled={reanalyzing}
            className="p-2 hover:bg-secondary text-muted-foreground hover:text-foreground rounded-xl transition-all disabled:opacity-50 active:scale-95 focus-ring"
            title="Reanalyze"
          >
            <RefreshCw className={`w-4 h-4 ${reanalyzing ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => onDeleteTask(task.id)}
            className="p-2 hover:bg-red-50 text-muted-foreground hover:text-red-500 rounded-xl transition-all active:scale-95 focus-ring"
            title="Delete Quest"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>

        <div className="pr-48">
          <div className="flex items-center gap-2 mb-2">
            {task.status === 'completed' && (
              <span className="text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-600 border border-emerald-100 px-2.5 py-1 rounded-lg flex items-center gap-1">
                <Award className="w-3.5 h-3.5" /> Completed
              </span>
            )}
          </div>
          <h2 className="text-xl md:text-2xl font-bold tracking-tight text-foreground">
            {task.title}
          </h2>
          {task.description && (
            <p className="text-xs md:text-sm text-muted-foreground/80 mt-2.5 leading-relaxed max-w-2xl font-medium">
              {task.description}
            </p>
          )}

          <div className="flex flex-wrap items-center gap-y-2 gap-x-4 mt-4 pt-4 border-t border-slate-100 text-xs text-muted-foreground">
            <span className="flex items-center gap-1.5 font-medium">
              <Calendar className="w-3.5 h-3.5 text-primary" /> Deadline: <strong className="text-foreground">{formatDate(task.deadline)}</strong>
            </span>
            <span className="hidden sm:inline text-border">•</span>
            <span className="flex items-center gap-1.5 font-medium">
              <Layers className="w-3.5 h-3.5 text-primary" /> <strong className="text-foreground">{sortedMissions.length}</strong> Milestones
            </span>
          </div>
        </div>
      </div>

      {/* Today's Mission & Focus Workspace */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-3">
          <h3 className="text-[12px] uppercase font-bold text-muted-foreground tracking-wider flex items-center gap-2">
            <Swords className="w-4 h-4 text-primary" /> Current Mission
          </h3>
          
          {activeMission ? (
            <MissionCard mission={activeMission} onComplete={onCompleteMission} />
          ) : task.status === 'completed' ? (
            <div className="card-elevated border-l-4 border-l-emerald-400 p-6 flex items-center justify-between min-h-[120px] bg-white">
              <div>
                <h4 className="font-bold text-sm text-foreground">All Missions Deployed</h4>
                <p className="text-xs text-muted-foreground mt-1">
                  Quest completed successfully under Atlas guidance.
                </p>
              </div>
              <Award className="w-8 h-8 text-emerald-500 shrink-0" />
            </div>
          ) : (
            <div className="card-elevated p-6 text-center text-sm text-muted-foreground bg-white">
              No active mission available.
            </div>
          )}
        </div>

        <div className="space-y-3">
          <h3 className="text-[12px] uppercase font-bold text-muted-foreground tracking-wider flex items-center gap-2">
            <Zap className="w-4 h-4 text-primary" /> Today's Focus
          </h3>
          
          {task.todays_mission && task.status !== 'completed' ? (
            <div className="card-elevated border-l-4 border-l-primary p-6 flex flex-col justify-between min-h-[120px] bg-gradient-to-br from-primary/[0.01] to-white">
              <div>
                <h4 className="font-bold text-sm text-foreground flex items-center gap-2">
                  <Target className="w-4 h-4 text-primary shrink-0" /> {task.todays_mission.title}
                </h4>
                <p className="text-xs text-muted-foreground mt-2 leading-relaxed font-medium">
                  <strong>Rationale:</strong> {task.todays_mission.reason}
                </p>
                <p className="text-xs text-primary/80 mt-1.5 font-semibold">
                  <strong>Benefit:</strong> {task.todays_mission.benefit}
                </p>
              </div>
              <div className="flex justify-between items-center mt-4 pt-3 border-t border-slate-100 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-primary" /> Est: <strong className="text-foreground font-semibold">{task.todays_mission.estimated_time}</strong>
                </span>
                <span className="text-primary font-bold text-[10px] uppercase tracking-wider bg-primary/10 px-2 py-0.5 rounded">High Priority</span>
              </div>
            </div>
          ) : task.status === 'completed' ? (
            <div className="card-elevated border-l-4 border-l-emerald-400 p-6 flex items-center justify-between min-h-[120px] bg-white">
              <div>
                <h4 className="font-bold text-sm text-foreground">Quest Complete</h4>
                <p className="text-xs text-muted-foreground mt-1">
                  All goals achieved. Take a well-deserved break.
                </p>
              </div>
              <Award className="w-8 h-8 text-emerald-500 shrink-0" />
            </div>
          ) : (
            <div className="card-elevated p-6 text-center text-sm text-muted-foreground bg-white">
              Atlas will recommend a focus when missions are available.
            </div>
          )}

          {/* AI Decision Timeline */}
          <div className="card-elevated overflow-hidden bg-white">
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="w-full flex items-center justify-between p-4.5 text-[12px] font-bold text-muted-foreground uppercase tracking-wider hover:bg-slate-50/50 transition-all text-left focus-ring"
            >
              <span className="flex items-center gap-2">
                <History className="w-4 h-4 text-primary" /> Decision Timeline
              </span>
              {isCollapsed ? <ChevronDown className="w-4 h-4 text-muted-foreground" /> : <ChevronUp className="w-4 h-4 text-muted-foreground" />}
            </button>
            
            {!isCollapsed && (
              <div className="p-5 pt-0 space-y-4 max-h-[320px] overflow-y-auto">
                {timelineEvents.length === 0 ? (
                  <div className="text-center text-sm text-muted-foreground py-6">
                    No timeline events recorded yet.
                  </div>
                ) : (
                  <div className="relative border-l border-slate-100 pl-5 ml-2.5 space-y-5">
                    {timelineEvents.map((event) => {
                      let Icon = Sparkles;
                      let iconColor = "text-primary";
                      let bgColor = "bg-primary/10";
                      let borderStyle = "border-primary/20";
                      
                      if (event.type === "goal_created") {
                        Icon = Compass; iconColor = "text-emerald-600"; bgColor = "bg-emerald-50"; borderStyle = "border-emerald-100";
                      } else if (event.type === "mission_chain_generated") {
                        Icon = Layers; iconColor = "text-blue-600"; bgColor = "bg-blue-50"; borderStyle = "border-blue-100";
                      } else if (event.type === "priority_calculated") {
                        Icon = Zap; iconColor = "text-amber-600"; bgColor = "bg-amber-50"; borderStyle = "border-amber-100";
                      } else if (event.type === "risk_evaluated") {
                        Icon = AlertTriangle; iconColor = "text-red-500"; bgColor = "bg-red-50"; borderStyle = "border-red-100";
                      } else if (event.type === "completion_probability_updated") {
                        Icon = Target; iconColor = "text-cyan-600"; bgColor = "bg-cyan-50"; borderStyle = "border-cyan-100";
                      } else if (event.type === "todays_mission_selected") {
                        Icon = Brain; iconColor = "text-violet-600"; bgColor = "bg-violet-50"; borderStyle = "border-violet-100";
                      } else if (event.type === "adaptive_reveal_updated") {
                        Icon = Sparkles; iconColor = "text-purple-600"; bgColor = "bg-purple-50"; borderStyle = "border-purple-100";
                      } else if (event.type === "recovery_plan_generated") {
                        Icon = AlertTriangle; iconColor = "text-red-600"; bgColor = "bg-red-50"; borderStyle = "border-red-100";
                      }
                      
                      return (
                        <div key={event.id} className="relative group text-left">
                          <div className={`absolute -left-[28.5px] top-0.5 ${bgColor} rounded-full p-1 border-2 border-white ${borderStyle} shadow-sm shrink-0 flex items-center justify-center`}>
                            <Icon className={`w-3 h-3 ${iconColor}`} />
                          </div>
                          <div className="flex flex-col gap-1">
                            <div className="flex items-center justify-between text-xs">
                              <span className="font-bold text-foreground">{event.title}</span>
                              <span className="text-[10px] font-semibold text-muted-foreground/60">{new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
                            </div>
                            <p className="text-xs text-muted-foreground/80 leading-relaxed font-medium">
                              {event.description}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Progress Tracker */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-[12px] uppercase font-bold text-muted-foreground tracking-wider flex items-center gap-2">
            <Compass className="w-4 h-4 text-primary" /> Quest Progress
          </h3>
          <span className="text-xs font-bold text-primary bg-primary/10 px-2.5 py-1 rounded-lg">
            {completedCount}/{sortedMissions.length} Milestones ({progressPct}%)
          </span>
        </div>

        <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-primary to-primary-light transition-all duration-500 rounded-full progress-animated"
            style={{ width: `${progressPct}%` }}
          />
        </div>

        {/* Assessment & Rescue */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 pt-2">
          <div className="md:col-span-6">
            <RiskIndicator
              priorityScore={task.priority_score}
              riskScore={task.risk_score}
              completionProbability={task.completion_probability}
              reason={task.risk_explanation}
            />
          </div>
          <div className="md:col-span-6">
            {task.risk_level === 'High' && task.rescue_plan ? (
              <RescuePanel rescuePlan={task.rescue_plan} />
            ) : (
              <div className="card-elevated p-6 flex flex-col justify-center items-center text-center h-full min-h-[160px] border-dashed border-slate-200/80 bg-white">
                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Recovery Strategy Standby
                </span>
                <p className="text-xs text-muted-foreground/80 max-w-[280px] mt-2.5 leading-relaxed font-medium">
                  Atlas Assessment reports stable parameters. No intervention required.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Atlas Insights */}
        {task.explanation && (
          <div className="card-elevated p-6 space-y-5 bg-white">
            <h3 className="text-[12px] uppercase font-bold text-muted-foreground tracking-wider flex items-center gap-2">
              <Brain className="w-4 h-4 text-primary" /> Atlas Insights
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                {task.explanation.why_this_priority && task.explanation.why_this_priority.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-foreground uppercase tracking-wider">Priority Rationale</h4>
                    <ul className="text-xs text-muted-foreground space-y-2">
                      {task.explanation.why_this_priority.map((item, idx) => (
                        <li key={idx} className="flex gap-2 items-start leading-relaxed font-medium">
                          <span className="w-1.5 h-1.5 rounded-full bg-violet-400 mt-1.5 shrink-0" />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {task.explanation.recommended_focus && task.explanation.recommended_focus.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-foreground uppercase tracking-wider">Recommended Focus</h4>
                    <ul className="text-xs text-muted-foreground space-y-2">
                      {task.explanation.recommended_focus.map((item, idx) => (
                        <li key={idx} className="flex gap-2 items-start leading-relaxed font-medium">
                          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              <div className="space-y-4">
                {task.explanation.current_risks && task.explanation.current_risks.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-foreground uppercase tracking-wider">Timeline Risks</h4>
                    <ul className="text-xs text-muted-foreground space-y-2">
                      {task.explanation.current_risks.map((item, idx) => (
                        <li key={idx} className="flex gap-2 items-start leading-relaxed font-medium">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {task.explanation.tasks_to_delay && task.explanation.tasks_to_delay.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-foreground uppercase tracking-wider">Scope Adjustments</h4>
                    <ul className="text-xs text-muted-foreground space-y-2">
                      {task.explanation.tasks_to_delay.map((item, idx) => (
                        <li key={idx} className="flex gap-2 items-start leading-relaxed font-medium">
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Atlas Productivity Profile */}
        <div className="card-elevated p-6 space-y-5 bg-white">
          <h3 className="text-[12px] uppercase font-bold text-muted-foreground tracking-wider flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-primary" /> Atlas Productivity Profile
          </h3>
          {task.atlas_profile ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <span className="text-[10px] uppercase font-bold tracking-wider bg-primary/10 text-primary px-2.5 py-1 rounded-lg">
                  Current Archetype
                </span>
                <h4 className="text-lg font-bold text-foreground">{task.atlas_profile.profile}</h4>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                <div className="bg-emerald-50/30 border border-emerald-100/60 rounded-2xl p-5 space-y-3 transition-all duration-300 hover:bg-emerald-50/50">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-600 block">Strengths</span>
                  <ul className="text-xs text-muted-foreground space-y-2">
                    {task.atlas_profile.strengths && task.atlas_profile.strengths.map((item, idx) => (
                      <li key={idx} className="flex gap-2 items-start leading-relaxed font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="bg-amber-50/30 border border-amber-100/60 rounded-2xl p-5 space-y-3 transition-all duration-300 hover:bg-amber-50/50">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-amber-600 block">Growth Areas</span>
                  <ul className="text-xs text-muted-foreground space-y-2">
                    {task.atlas_profile.weaknesses && task.atlas_profile.weaknesses.map((item, idx) => (
                      <li key={idx} className="flex gap-2 items-start leading-relaxed font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="bg-blue-50/30 border border-blue-100/60 rounded-2xl p-5 space-y-3 transition-all duration-300 hover:bg-blue-50/50">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 block">Recommendations</span>
                  <ul className="text-xs text-muted-foreground space-y-2">
                    {task.atlas_profile.recommendations && task.atlas_profile.recommendations.map((item, idx) => (
                      <li key={idx} className="flex gap-2 items-start leading-relaxed font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-sm text-muted-foreground py-10 border border-dashed border-slate-200/80 rounded-2xl bg-slate-50/30">
              <Sparkles className="w-6 h-6 text-muted-foreground/35 mx-auto mb-2.5 animate-pulse" />
              <p className="font-semibold text-foreground/80">Observing execution patterns...</p>
              <p className="text-xs text-muted-foreground/60 max-w-[280px] mx-auto mt-1 leading-relaxed">
                Atlas is building your archetype. Complete a quest to unlock your productivity profile.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Locked Missions */}
      <div className="space-y-3">
        <h3 className="text-[12px] uppercase font-bold text-muted-foreground tracking-wider flex items-center gap-2">
          <EyeOff className="w-4 h-4 text-primary" /> Milestones &amp; Atlas Guidance
        </h3>
        
        {previewMissions.length === 0 ? (
          <div className="py-10 border border-dashed border-slate-200/80 text-center rounded-2xl bg-slate-50/30 text-sm text-muted-foreground">
            No additional milestones to display.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {previewMissions.map((mission) => (
              <MissionCard key={mission.id} mission={mission} onComplete={null} />
            ))}
          </div>
        )}
      </div>

      {/* Simulation Modal */}
      {isSimulationOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-md p-4 overflow-y-auto">
          <div className="bg-white border border-slate-100 rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-[0_24px_64px_rgba(0,0,0,0.08)] flex flex-col animate-mission-unlock">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-primary/10 rounded-xl">
                  <Brain className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="text-base font-extrabold text-foreground tracking-tight">Atlas Simulation</h3>
                  <p className="text-[11px] font-semibold text-muted-foreground/80">What-if scenario planner</p>
                </div>
              </div>
              <button
                onClick={() => setIsSimulationOpen(false)}
                className="p-2 hover:bg-slate-100 text-muted-foreground hover:text-foreground rounded-xl transition-all focus-ring"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 grid grid-cols-1 md:grid-cols-12 gap-8 text-left">
              {/* Left: Parameters */}
              <div className="md:col-span-5 space-y-6 md:border-r md:border-slate-100 md:pr-8">
                <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Parameters</h4>
                
                <div className="space-y-2">
                  <label className="text-xs font-bold text-foreground uppercase tracking-wider block">Simulated Deadline</label>
                  <input
                    type="date"
                    value={simulatedDeadline}
                    onChange={(e) => setSimulatedDeadline(e.target.value)}
                    className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-medium text-foreground"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold text-foreground uppercase tracking-wider block">Available Hours / Day</label>
                  <input
                    type="number"
                    min="1"
                    max="24"
                    value={availableHours}
                    onChange={(e) => setAvailableHours(Number(e.target.value))}
                    className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all font-medium text-foreground"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold text-foreground uppercase tracking-wider block">Milestone Completion</label>
                  <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
                    {sortedMissions.map((m) => {
                      const isChecked = simulatedMissions.includes(m.id);
                      return (
                        <label key={m.id} className={`flex items-start gap-3 p-3 border rounded-xl cursor-pointer transition-all text-xs text-left ${
                          isChecked 
                            ? 'border-emerald-100 bg-emerald-50/20' 
                            : 'border-slate-100 bg-slate-50/30 hover:border-slate-200 hover:bg-slate-50/50'
                        }`}>
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => {
                              if (isChecked) {
                                setSimulatedMissions(simulatedMissions.filter(id => id !== m.id));
                              } else {
                                setSimulatedMissions([...simulatedMissions, m.id]);
                              }
                            }}
                            className="mt-0.5 rounded border-slate-300 text-primary focus:ring-primary focus:ring-offset-0 focus:ring-2"
                          />
                          <span className={`leading-snug select-none font-semibold ${isChecked ? 'text-emerald-800/60 line-through' : 'text-foreground'}`}>
                            {m.title}
                          </span>
                        </label>
                      );
                    })}
                  </div>
                </div>

                <button
                  onClick={handleRunSimulation}
                  disabled={simulating}
                  className="w-full py-3 bg-primary hover:bg-primary-light text-white font-bold text-xs uppercase tracking-wider rounded-xl transition-all duration-200 disabled:opacity-50 active:scale-[0.98] shadow-md shadow-primary/10 flex items-center justify-center gap-1.5 focus-ring"
                >
                  {simulating ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin text-white" />
                      <span>Running simulation...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 text-white" />
                      <span>Run Simulation</span>
                    </>
                  )}
                </button>
                
                {simError && (
                  <p className="text-xs text-red-500 text-center font-medium mt-2">{simError}</p>
                )}
              </div>

              {/* Right: Results */}
              <div className="md:col-span-7 flex flex-col justify-start">
                {simulationResult ? (
                  <div className="space-y-6 text-left animate-mission-unlock">
                    <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Simulation Forecast</h4>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {/* Risk Score */}
                      <div className="bg-white border border-slate-100 rounded-2xl p-5 flex flex-col shadow-[0_4px_16px_rgba(0,0,0,0.015)]">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Timeline Risk</span>
                        <div className="flex items-baseline gap-2 mt-2">
                          <span className="text-muted-foreground text-xs line-through">{task.risk_score}/100</span>
                          <span className="text-foreground font-semibold text-sm">→</span>
                          <span className={`text-2xl font-extrabold ${
                            simulationResult.new_risk_score >= 70 ? 'text-red-500' :
                            simulationResult.new_risk_score >= 40 ? 'text-amber-500' : 'text-emerald-500'
                          }`}>
                            {simulationResult.new_risk_score}/100
                          </span>
                        </div>
                        <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-lg mt-3 self-start ${
                          simulationResult.risk_level === 'High' ? 'bg-red-50 text-red-600 border border-red-100' :
                          simulationResult.risk_level === 'Medium' ? 'bg-amber-50 text-amber-600 border border-amber-100' :
                          'bg-emerald-50 text-emerald-600 border border-emerald-100'
                        }`}>
                          {simulationResult.risk_level} Risk
                        </span>
                      </div>

                      {/* Completion Probability */}
                      <div className="bg-white border border-slate-100 rounded-2xl p-5 flex flex-col shadow-[0_4px_16px_rgba(0,0,0,0.015)]">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Completion Chance</span>
                        <div className="flex items-baseline gap-2 mt-2">
                          <span className="text-muted-foreground text-xs line-through">{Math.round(task.completion_probability * 100)}%</span>
                          <span className="text-foreground font-semibold text-sm">→</span>
                          <span className={`text-2xl font-extrabold ${
                            simulationResult.new_completion_probability >= 75 ? 'text-emerald-500' :
                            simulationResult.new_completion_probability >= 40 ? 'text-amber-500' : 'text-red-500'
                          }`}>
                            {simulationResult.new_completion_probability}%
                          </span>
                        </div>
                        <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden mt-4">
                          <div
                            className={`h-full transition-all duration-500 rounded-full ${
                              simulationResult.new_completion_probability >= 75 ? 'bg-emerald-500' :
                              simulationResult.new_completion_probability >= 40 ? 'bg-amber-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${simulationResult.new_completion_probability}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Coaching Review */}
                    <div className="bg-indigo-50/15 border border-indigo-100/40 rounded-2xl p-5 space-y-3">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-primary">Atlas Coaching Review</span>
                      <p className="text-sm text-muted-foreground/90 leading-relaxed font-medium">
                        {simulationResult.summary}
                      </p>
                      
                      {simulationResult.recommendations && simulationResult.recommendations.length > 0 && (
                        <div className="space-y-2.5 pt-3.5 border-t border-slate-200/50">
                          <span className="text-xs font-bold text-foreground uppercase tracking-wider">Recommendations</span>
                          <ul className="text-xs text-muted-foreground space-y-2">
                            {simulationResult.recommendations.map((rec, idx) => (
                              <li key={idx} className="flex gap-2 items-start leading-relaxed font-medium">
                                <span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" />
                                <span>{rec}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {/* Recovery Timeline */}
                    {simulationResult.recommended_schedule && simulationResult.recommended_schedule.length > 0 && (
                      <div className="space-y-3 pt-2">
                        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Recovery Timeline</span>
                        <div className="relative border-l border-slate-100 pl-5 ml-2.5 space-y-4">
                          {simulationResult.recommended_schedule.map((step, idx) => (
                            <div key={idx} className="relative text-left">
                              <div className="absolute -left-[24.5px] top-1.5 w-2 h-2 bg-primary rounded-full border-2 border-white" />
                              <p className="text-xs text-foreground font-semibold leading-relaxed">
                                {step}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full min-h-[300px] text-center border border-dashed border-slate-200/80 rounded-2xl bg-slate-50/30">
                    <Sparkles className="w-8 h-8 text-muted-foreground/30 mb-3 animate-pulse" />
                    <p className="text-sm font-bold text-foreground/80">Ready for simulation</p>
                    <p className="text-xs text-muted-foreground/60 max-w-[260px] mt-1.5 leading-relaxed font-medium">
                      Adjust parameters and click <strong>Run Simulation</strong> to see how changes affect your timeline.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
