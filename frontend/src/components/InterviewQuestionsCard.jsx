import React, { useState } from 'react';
import { Copy, Check, Compass } from 'lucide-react';

export default function InterviewQuestionsCard({ questions = [] }) {
  const [copiedIdx, setCopiedIdx] = useState(null);

  if (!questions || questions.length === 0) {
    return null;
  }

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <div className="glass-panel interview-questions-card">
      <div className="section-header">
        <div className="section-title-group">
          <div>
            <h2 className="section-title">Interview questions</h2>
            <p className="section-subtitle">
              Questions to probe the gaps identified above
            </p>
          </div>
        </div>
      </div>

      <div className="questions-grid">
        {questions.map((item, idx) => {
          const isObj = typeof item === 'object' && item !== null;
          const skill = isObj ? item.skill : `Competency #${idx + 1}`;
          const category = isObj ? item.category : 'Technical Probe';
          const questionText = isObj ? item.question : item;

          return (
            <div key={idx} className="question-item-card">
              <div className="question-header">
                <div className="question-meta">
                  <span className="pill pill-warning question-skill-pill">
                    Target: {skill}
                  </span>
                  <span className="pill pill-neutral question-cat-pill">
                    {category}
                  </span>
                </div>
                <button
                  type="button"
                  className="btn-icon-ghost"
                  onClick={() => handleCopy(questionText, idx)}
                  title="Copy question to clipboard"
                >
                  {copiedIdx === idx ? (
                    <Check size={14} className="text-emerald" />
                  ) : (
                    <Copy size={14} />
                  )}
                </button>
              </div>

              <p className="question-content">"{questionText}"</p>

              <div className="question-probe-tip">
                <Compass size={13} className="text-cyan" />
                <span className="probe-tip-text">
                  <strong>Tip:</strong> ask for a concrete example, not a definition — listen for real trade-offs and what went wrong.
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
