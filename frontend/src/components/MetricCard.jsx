import React from 'react';
import { AlertCircle, ShieldAlert, Sparkles, TrendingUp } from 'lucide-react';

export default function MetricCard({ title, value, maxValue = 100, type, explanation }) {
  // Determine color theme based on score/type
  const getColors = () => {
    if (type === 'priority') {
      if (value > 75) return { text: 'text-rose-500', bg: 'bg-rose-950/20', border: 'border-rose-900/30', circle: '#f43f5e', glow: 'glow-rose' };
      if (value > 40) return { text: 'text-amber-500', bg: 'bg-amber-950/20', border: 'border-amber-900/30', circle: '#f59e0b', glow: 'glow-yellow' };
      return { text: 'text-blue-500', bg: 'bg-blue-950/20', border: 'border-blue-900/30', circle: '#3b82f6', glow: 'glow-blue' };
    }
    
    if (type === 'risk') {
      if (value > 70) return { text: 'text-rose-500', bg: 'bg-rose-950/20', border: 'border-rose-900/30', circle: '#f43f5e', glow: 'glow-rose' };
      if (value > 30) return { text: 'text-amber-500', bg: 'bg-amber-950/20', border: 'border-amber-900/30', circle: '#f59e0b', glow: 'glow-yellow' };
      return { text: 'text-emerald-500', bg: 'bg-emerald-950/20', border: 'border-emerald-900/30', circle: '#10b981', glow: 'glow-green' };
    }
    
    if (type === 'probability') {
      const pct = value * 100;
      if (pct > 75) return { text: 'text-emerald-500', bg: 'bg-emerald-950/20', border: 'border-emerald-900/30', circle: '#10b981', glow: 'glow-green' };
      if (pct > 40) return { text: 'text-amber-500', bg: 'bg-amber-950/20', border: 'border-amber-900/30', circle: '#f59e0b', glow: 'glow-yellow' };
      return { text: 'text-rose-500', bg: 'bg-rose-950/20', border: 'border-rose-900/30', circle: '#f43f5e', glow: 'glow-rose' };
    }

    return { text: 'text-[#fafafa]', bg: 'bg-secondary', border: 'border-border', circle: '#a1a1aa', glow: '' };
  };

  const colors = getColors();
  const percentage = type === 'probability' ? value * 100 : (value / maxValue) * 100;
  
  // SVG Gauge specifications
  const radius = 32;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const getIcon = () => {
    switch (type) {
      case 'priority': return <Sparkles className="w-4 h-4" />;
      case 'risk': return <ShieldAlert className="w-4 h-4" />;
      case 'probability': return <TrendingUp className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  const getDisplayValue = () => {
    if (type === 'probability') {
      return `${Math.round(value * 100)}%`;
    }
    return Math.round(value);
  };

  return (
    <div className={`glass-panel rounded-xl p-5 border ${colors.border} ${colors.bg} ${colors.glow} flex flex-col justify-between transition-all duration-300 hover:scale-[1.02] min-h-[170px]`}>
      <div className="flex justify-between items-start">
        <div>
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block mb-1">
            {title}
          </span>
          <div className="flex items-center gap-1.5 font-bold text-lg text-foreground">
            <span className={colors.text}>{getIcon()}</span>
            <span>{type === 'risk' && value > 70 ? 'CRITICAL' : type === 'risk' && value > 30 ? 'CAUTION' : type === 'risk' ? 'STABLE' : ''}</span>
            <span>{type === 'probability' && value > 0.75 ? 'HIGH CHANCE' : type === 'probability' && value > 0.4 ? 'VIABLE' : type === 'probability' ? 'AT RISK' : ''}</span>
            <span>{type === 'priority' && value > 75 ? 'LEGENDARY' : type === 'priority' && value > 40 ? 'EPIC' : type === 'priority' ? 'COMMON' : ''}</span>
          </div>
        </div>

        {/* Circular Gauge */}
        <div className="relative w-16 h-16 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90">
            {/* Background track circle */}
            <circle
              cx="32"
              cy="32"
              r={radius}
              stroke="rgba(255, 255, 255, 0.05)"
              strokeWidth="5"
              fill="transparent"
            />
            {/* Animated foreground value circle */}
            <circle
              cx="32"
              cy="32"
              r={radius}
              stroke={colors.circle}
              strokeWidth="5"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-700 ease-out"
            />
          </svg>
          <span className="absolute text-sm font-bold font-mono">
            {getDisplayValue()}
          </span>
        </div>
      </div>

      {explanation && (
        <p className="text-xs text-muted-foreground line-clamp-3 mt-4 border-t border-white/5 pt-3 leading-relaxed">
          {explanation}
        </p>
      )}
    </div>
  );
}
