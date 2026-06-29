import React, { useState } from 'react';
import { Target, Calendar, ListTodo, Plus, Loader2, ArrowLeft } from 'lucide-react';

export default function TaskCreation({ onSubmit, isLoading, onBack }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [deadline, setDeadline] = useState('');

  const suggestions = [
    { title: "Complete Thesis Draft", desc: "Write introduction, methods, results and conclusion. Check citations.", days: 7 },
    { title: "Deploy Hackathon Landing Page", desc: "Build UI in React, connect backend API, deploy on Vercel.", days: 1 },
    { title: "Prepare for System Design Interview", desc: "Study load balancers, caching, DB sharding, and write notes.", days: 3 }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title || !deadline) return;

    onSubmit({
      title,
      description,
      deadline: new Date(deadline).toISOString()
    });
  };

  const handleSuggestionClick = (sug) => {
    setTitle(sug.title);
    setDescription(sug.desc);
    
    const date = new Date();
    date.setDate(date.getDate() + sug.days);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    setDeadline(`${year}-${month}-${day}T12:00`);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3 mb-2">
        <button
          onClick={onBack}
          className="p-2.5 hover:bg-slate-50 rounded-xl text-muted-foreground hover:text-foreground transition-all active:scale-95 border border-slate-100 bg-white focus-ring shadow-sm"
          title="Back to Dashboard"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div>
          <h2 className="text-xl font-bold tracking-tight text-foreground">Create New Quest</h2>
          <p className="text-xs text-muted-foreground">Atlas will decompose your goal into actionable milestones</p>
        </div>
      </div>

      <div className="card-elevated p-8 bg-white">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-1.5">
            <label className="block text-xs font-bold text-foreground uppercase tracking-wider">
              Goal / Objective
            </label>
            <input
              type="text"
              required
              placeholder="What do you want to accomplish?"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={isLoading}
              className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all disabled:opacity-50 text-foreground placeholder:text-muted-foreground/60 font-semibold"
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-bold text-foreground uppercase tracking-wider">
              Description <span className="text-muted-foreground font-semibold text-[10px] lowercase">(optional)</span>
            </label>
            <textarea
              rows="3"
              placeholder="Add context, resources, or specific deliverables..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isLoading}
              className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all disabled:opacity-50 text-foreground resize-none placeholder:text-muted-foreground/60 font-semibold"
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-bold text-foreground uppercase tracking-wider">
              Deadline
            </label>
            <div className="relative">
              <input
                type="datetime-local"
                required
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                disabled={isLoading}
                className="w-full bg-slate-50/50 border border-slate-200 rounded-xl pl-11 pr-4 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all disabled:opacity-50 text-foreground font-semibold"
              />
              <Calendar className="w-4 h-4 text-muted-foreground absolute left-4 top-1/2 -translate-y-1/2" />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading || !title || !deadline}
            className="w-full bg-primary hover:bg-primary-light text-white font-bold text-xs uppercase tracking-wider py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all duration-200 shadow-md shadow-primary/10 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none focus-ring"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" /> Atlas is analyzing your goal...
              </>
            ) : (
              <>
                <Plus className="w-4 h-4 text-white" /> Create Quest
              </>
            )}
          </button>
        </form>

        {!isLoading && (
          <div className="mt-8 pt-6 border-t border-slate-100">
            <span className="text-xs font-bold text-foreground uppercase tracking-wider block mb-3.5 flex items-center gap-1.5">
              <ListTodo className="w-4 h-4 text-primary" /> Quick Start Templates
            </span>
            <div className="grid grid-cols-1 gap-3">
              {suggestions.map((sug, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestionClick(sug)}
                  className="w-full text-left p-4 rounded-2xl border border-slate-100 bg-white hover:bg-slate-50/50 hover:border-primary/25 hover:shadow-[0_4px_20px_rgba(0,0,0,0.015)] transition-all flex justify-between items-center group text-sm focus-ring"
                >
                  <div className="pr-4 truncate flex-1">
                    <span className="font-bold text-foreground group-hover:text-primary transition-colors block truncate">
                      {sug.title}
                    </span>
                    <p className="text-xs text-muted-foreground/80 truncate mt-1 leading-relaxed font-medium">
                      {sug.desc}
                    </p>
                  </div>
                  <span className="text-[10px] font-bold bg-primary/10 text-primary px-2.5 py-1 rounded-lg shrink-0">
                    {sug.days} Days
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
