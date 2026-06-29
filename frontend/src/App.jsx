import React, { useState, useEffect } from 'react';
import TaskCard from './components/TaskCard';
import TaskCreation from './pages/TaskCreation';
import Dashboard from './pages/Dashboard';
import { 
  Trophy, 
  Layers, 
  Compass, 
  RefreshCw, 
  AlertTriangle, 
  Plus, 
  Sparkles, 
  FolderPlus
} from 'lucide-react';

const API_BASE = '/api';

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [activePage, setActivePage] = useState('dashboard'); // 'dashboard' | 'create'
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch all tasks from the Flask backend
  const fetchTasks = async (selectId = null) => {
    try {
      const res = await fetch(`${API_BASE}/tasks`);
      if (!res.ok) throw new Error("Failed to load tasks");
      const data = await res.json();
      setTasks(data);
      
      // Auto-select tasks
      if (data.length > 0) {
        if (selectId) {
          const found = data.find(t => t.id === selectId);
          setSelectedTask(found || data[0]);
        } else if (selectedTask) {
          const found = data.find(t => t.id === selectedTask.id);
          setSelectedTask(found || data[0]);
        } else {
          setSelectedTask(data[0]);
        }
      } else {
        setSelectedTask(null);
      }
    } catch (err) {
      console.error(err);
      setError("Could not connect to Flask backend. Please verify your server is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  // Handle task creation
  const handleCreateTask = async (taskPayload) => {
    setIsCreating(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskPayload)
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || "Failed to decompose goal");
      }
      const newTask = await res.json();
      
      // Select the new task and navigate to dashboard
      await fetchTasks(newTask.id);
      setActivePage('dashboard');
    } catch (err) {
      console.error(err);
      setError(err.message || "Error calling Atlas decomposition. Make sure your API key is configured.");
    } finally {
      setIsCreating(false);
    }
  };

  // Handle mission completion
  const handleCompleteMission = async (missionId) => {
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/missions/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mission_id: missionId })
      });
      if (!res.ok) throw new Error("Failed to update mission");
      const updatedTask = await res.json();
      
      // Update local task state smoothly
      setTasks(prev => prev.map(t => t.id === updatedTask.id ? updatedTask : t));
      setSelectedTask(updatedTask);
    } catch (err) {
      console.error(err);
      setError("Error marking mission complete.");
    }
  };

  // Handle task deletion
  const handleDeleteTask = async (taskId) => {
    if (!window.confirm("Are you sure you want to delete this quest? This will remove all decomposed missions.")) return;
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
        method: 'DELETE'
      });
      if (!res.ok) throw new Error("Failed to delete task");
      
      await fetchTasks();
      setActivePage('dashboard');
    } catch (err) {
      console.error(err);
      setError("Error deleting quest.");
    }
  };

  // Handle force Atlas assessment
  const handleReanalyze = async (taskId) => {
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/tasks/${taskId}/reanalyze`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error("Failed to run Atlas assessment");
      const updatedTask = await res.json();
      
      setTasks(prev => prev.map(t => t.id === updatedTask.id ? updatedTask : t));
      setSelectedTask(updatedTask);
    } catch (err) {
      console.error(err);
      setError("Error running Atlas assessment.");
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-foreground relative overflow-x-hidden">
      
      {/* Header bar */}
      <header className="border-b border-border bg-white/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div 
            className="flex items-center gap-3 cursor-pointer select-none group"
            onClick={() => setActivePage('dashboard')}
          >
            <div className="h-9 w-9 rounded-xl bg-primary flex items-center justify-center shadow-md shadow-primary/20 group-hover:shadow-lg group-hover:shadow-primary/25 transition-all">
              <Compass className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight text-foreground">
                QuestFlow <span className="text-primary font-semibold text-xs bg-primary/8 px-2 py-0.5 rounded-md ml-1">Atlas</span>
              </span>
              <p className="text-[11px] text-muted-foreground hidden sm:block -mt-0.5">AI Executive Productivity Coach</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setActivePage('create')}
              className="flex items-center gap-1.5 bg-primary hover:bg-primary-light text-white text-[13px] font-semibold py-2 px-4 rounded-xl transition-all active:scale-[0.97] shadow-md shadow-primary/15 hover:shadow-lg hover:shadow-primary/20 focus-ring"
            >
              <Plus className="w-4 h-4" /> New Quest
            </button>
            <button 
              onClick={() => fetchTasks(selectedTask?.id)}
              className="p-2 hover:bg-secondary rounded-xl text-muted-foreground hover:text-foreground transition-all active:scale-95 focus-ring"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Container Layout */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative">
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl flex items-center gap-3 text-sm shadow-soft">
            <AlertTriangle className="w-5 h-5 shrink-0 text-red-500" />
            <div className="flex-1">{error}</div>
            <button onClick={() => setError(null)} className="text-xs font-semibold text-red-500 hover:text-red-700 hover:underline focus-ring px-2 py-1 rounded-lg">
              Dismiss
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* LEFT SIDEBAR: Active Quest Navigator */}
          <div className="lg:col-span-4 space-y-6">
            <div className="card-elevated p-5 flex flex-col gap-4">
              <div className="flex justify-between items-center">
                <h3 className="text-[13px] font-semibold text-foreground flex items-center gap-2">
                  <Layers className="w-4 h-4 text-primary" /> Quests
                  <span className="text-muted-foreground font-normal text-xs ml-0.5">({tasks.length})</span>
                </h3>
              </div>

              {loading ? (
                <div className="space-y-3">
                  <div className="skeleton h-[72px] w-full" />
                  <div className="skeleton h-[72px] w-full" />
                  <div className="skeleton h-[72px] w-full" />
                </div>
              ) : tasks.length === 0 ? (
                <div className="py-12 text-center rounded-xl bg-[#F8FAFC] border border-dashed border-border text-sm text-muted-foreground leading-relaxed px-6">
                  <Compass className="w-8 h-8 text-muted-foreground/40 mx-auto mb-3" />
                  <p className="font-medium text-foreground/70">No active quests yet</p>
                  <p className="text-xs mt-1">Click <strong>New Quest</strong> to get started with Atlas.</p>
                </div>
              ) : (
                <div className="space-y-2.5 max-h-[520px] overflow-y-auto pr-1">
                  {tasks.map((task) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      isSelected={selectedTask && selectedTask.id === task.id && activePage === 'dashboard'}
                      onClick={() => {
                        setSelectedTask(task);
                        setActivePage('dashboard');
                      }}
                      onDelete={handleDeleteTask}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* RIGHT VIEWPORT: Active Page Renderer */}
          <div className="lg:col-span-8">
            {activePage === 'create' ? (
              <TaskCreation 
                onSubmit={handleCreateTask} 
                isLoading={isCreating} 
                onBack={() => setActivePage('dashboard')} 
              />
            ) : selectedTask ? (
              <Dashboard
                task={selectedTask}
                onCompleteMission={handleCompleteMission}
                onReanalyze={handleReanalyze}
                onDeleteTask={handleDeleteTask}
              />
            ) : (
              /* Empty state view */
              <div className="card-elevated p-16 text-center flex flex-col items-center justify-center min-h-[450px]">
                <div className="p-5 rounded-2xl bg-primary/8 text-primary mb-6">
                  <Trophy className="w-10 h-10" />
                </div>
                
                <h3 className="text-xl font-bold text-foreground tracking-tight">Start your first quest</h3>
                <p className="text-sm text-muted-foreground max-w-sm mt-2 leading-relaxed">
                  Atlas will decompose your goal into a progressive chain of actionable milestones, track risk, and coach you through completion.
                </p>

                <button
                  onClick={() => setActivePage('create')}
                  className="mt-8 flex items-center gap-1.5 bg-primary hover:bg-primary-light text-white text-sm font-semibold py-2.5 px-5 rounded-xl transition-all active:scale-[0.97] shadow-md shadow-primary/15 focus-ring"
                >
                  <Plus className="w-4 h-4" /> New Quest
                </button>

                <div className="flex flex-wrap gap-3 justify-center items-center mt-10 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1.5 bg-secondary border border-border px-3 py-1.5 rounded-xl">
                    <Sparkles className="w-3.5 h-3.5 text-primary" /> AI Decomposition
                  </span>
                  <span className="flex items-center gap-1.5 bg-secondary border border-border px-3 py-1.5 rounded-xl">
                    <Layers className="w-3.5 h-3.5 text-primary" /> Progressive Reveal
                  </span>
                </div>
              </div>
            )}
          </div>

        </div>

      </main>

      {/* Footer bar */}
      <footer className="border-t border-border mt-16 py-8 bg-white/50">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-muted-foreground">
          QuestFlow Atlas &copy; 2026 &middot; Powered by Atlas, your executive productivity coach.
        </div>
      </footer>

    </div>
  );
}
