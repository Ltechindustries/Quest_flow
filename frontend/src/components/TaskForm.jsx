import React, { useState } from 'react';
import { Target, Calendar, ListTodo, Plus, Loader2 } from 'lucide-react';

export default function TaskForm({ onSubmit, isLoading }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [deadline, setDeadline] = useState('');

  // Default suggestions to help the user get started quickly
  const suggestions = [
    { title: "Complete Thesis Draft", desc: "Write introduction, methods, results and conclusion. Check citations.", days: 7 },
    { title: "Deploy Hackathon Landing Page", desc: "Build UI in React, connect backend API, deploy on Vercel.", days: 1 },
    { title: "Prepare for System Design Interview", desc: "Study load balancers, caching, DB sharding, and write notes.", days: 3 }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title || !deadline) return;
    
    // Format deadline to local ISO format for DB consistency
    onSubmit({
      title,
      description,
      deadline: new Date(deadline).toISOString()
    });
    
    // Reset form
    setTitle('');
    setDescription('');
    setDeadline('');
  };

  const handleSuggestionClick = (sug) => {
    setTitle(sug.title);
    setDescription(sug.desc);
    
    const date = new Date();
    date.setDate(date.getDate() + sug.days);
    // Format to local datetime-local input string: YYYY-MM-DDThh:mm
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    setDeadline(`${year}-${month}-${day}T12:00`);
  };

  return (
    <div className="glass-panel rounded-xl p-6 glow-rose">
      <h2 className="text-xl font-bold flex items-center gap-2 mb-4 text-[#fafafa]">
        <Target className="w-5 h-5 text-primary" /> Initialize New Quest
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
            Goal / Objective
          </label>
          <input
            type="text"
            required
            placeholder="e.g. Launch QuestFlow App"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={isLoading}
            className="w-full bg-[#0c0c0e] border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all disabled:opacity-50 text-foreground"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
            Details & Context (Optional)
          </label>
          <textarea
            rows="3"
            placeholder="Add details, resources, or specific subgoals..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isLoading}
            className="w-full bg-[#0c0c0e] border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all disabled:opacity-50 text-foreground resize-none"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
            Quest Deadline
          </label>
          <div className="relative">
            <input
              type="datetime-local"
              required
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              disabled={isLoading}
              className="w-full bg-[#0c0c0e] border border-border rounded-lg pl-10 pr-3 py-2 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all disabled:opacity-50 text-foreground"
            />
            <Calendar className="w-4 h-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !title || !deadline}
          className="w-full bg-primary hover:bg-[#ff5a79] text-white font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" /> Atlas is decomposing objective...
            </>
          ) : (
            <>
              <Plus className="w-4 h-4" /> Forge Quest & Missions
            </>
          )}
        </button>
      </form>

      {!isLoading && (
        <div className="mt-6 pt-5 border-t border-border">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-2 flex items-center gap-1.5">
            <ListTodo className="w-3.5 h-3.5" /> Quick Start Templates
          </span>
          <div className="space-y-2">
            {suggestions.map((sug, idx) => (
              <button
                key={idx}
                onClick={() => handleSuggestionClick(sug)}
                className="w-full text-left p-2.5 rounded-lg border border-border bg-[#0d0d10] hover:bg-[#18181c] transition-all flex justify-between items-center group text-xs"
              >
                <div>
                  <span className="font-semibold text-foreground group-hover:text-primary transition-all">
                    {sug.title}
                  </span>
                  <p className="text-[10px] text-muted-foreground line-clamp-1 mt-0.5">
                    {sug.desc}
                  </p>
                </div>
                <span className="text-[10px] bg-secondary text-muted-foreground px-2 py-0.5 rounded font-mono">
                  {sug.days}d
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
