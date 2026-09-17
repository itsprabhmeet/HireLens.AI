import React, { useState } from 'react';
import { HelpCircle, Copy, Check, MessageSquare, Compass } from 'lucide-react';

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
          <div className="section-icon-badge">
            <MessageSquare size={18} className="text-emerald" />
          </div>
          <div>
            <h2 className="section-title">Targeted Interview Questions</h2>
            <p className="section-subtitle">
              AI-generated technical probes specifically designed to verify candidate depth on identified gaps
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
                  <strong>Interviewer Note:</strong> Probe for concrete production examples, architectural trade-offs, and how they handled failure scenarios.
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
