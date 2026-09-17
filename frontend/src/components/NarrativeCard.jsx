import React from 'react';
import {
  FileCheck2,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  Sparkles,
} from 'lucide-react';

export default function NarrativeCard({ narrative = {} }) {
  const {
    verdict = 'Analysis complete.',
    overall_fit = 'Evaluated',
    strengths = [],
    gaps = [],
    suggestions = [],
  } = narrative || {};

  const toList = (val) => {
    if (Array.isArray(val)) return val.filter(Boolean);
    if (typeof val === 'string' && val.trim()) {
      return val.split(/\n+|(?<=[.!?])\s+/).map((s) => s.replace(/^[-•\s]+/, '').trim()).filter(Boolean);
    }
    return [];
  };

  const safeStrengths = toList(strengths);
  const safeGaps = toList(gaps);
  const safeSuggestions = toList(suggestions);

  return (
    <div className="glass-panel narrative-card">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-icon-badge">
            <Sparkles size={18} className="text-violet" />
          </div>
          <div>
            <h2 className="section-title">Executive Recruiter Assessment</h2>
            <p className="section-subtitle">
              Synthesized qualitative evaluation highlighting candidate strengths, risks, and next steps
            </p>
          </div>
        </div>
      </div>

      {/* Primary Verdict Callout */}
      <div className="verdict-banner">
        <div className="verdict-icon-col">
          <FileCheck2 size={24} className="text-indigo" />
        </div>
        <div className="verdict-text-col">
          <span className="verdict-headline">AI Recruiter Synthesis</span>
          <p className="verdict-body">{verdict}</p>
        </div>
      </div>

      {/* Grid of Strengths & Gaps */}
      <div className="assessment-grid">
        {/* Key Strengths */}
        <div className="assessment-column strengths-col">
          <div className="column-header">
            <CheckCircle2 size={16} className="text-emerald" />
            <h3 className="column-title text-emerald">Demonstrated Strengths ({safeStrengths.length})</h3>
          </div>
          <ul className="assessment-list">
            {safeStrengths.length > 0 ? (
              safeStrengths.map((item, idx) => (
                <li key={idx} className="assessment-item strength-item">
                  <span className="bullet-dot bullet-dot-emerald" />
                  <span className="assessment-text">{item}</span>
                </li>
              ))
            ) : (
              <li className="assessment-empty">No critical strengths detected in candidate text.</li>
            )}
          </ul>
        </div>

        {/* Areas for Growth / Gaps */}
        <div className="assessment-column gaps-col">
          <div className="column-header">
            <AlertTriangle size={16} className="text-warning" />
            <h3 className="column-title text-warning">Identified Competency Gaps ({safeGaps.length})</h3>
          </div>
          <ul className="assessment-list">
            {safeGaps.length > 0 ? (
              safeGaps.map((item, idx) => (
                <li key={idx} className="assessment-item gap-item">
                  <span className="bullet-dot bullet-dot-warning" />
                  <span className="assessment-text">{item}</span>
                </li>
              ))
            ) : (
              <li className="assessment-empty">No severe competency gaps detected against this JD.</li>
            )}
          </ul>
        </div>
      </div>

      {/* Recruiter Actionable Suggestions */}
      {safeSuggestions.length > 0 && (
        <div className="suggestions-box">
          <div className="suggestions-header">
            <Lightbulb size={16} className="text-cyan" />
            <h3 className="suggestions-title text-cyan">Actionable Hiring Recommendations</h3>
          </div>
          <div className="suggestions-chips-grid">
            {safeSuggestions.map((sug, idx) => (
              <div key={idx} className="suggestion-item">
                <span className="suggestion-index">{idx + 1}</span>
                <span className="suggestion-text">{sug}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
