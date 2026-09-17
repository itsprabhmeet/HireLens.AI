import React from 'react';
import { Briefcase, Sparkles, RotateCcw, FileText } from 'lucide-react';
import { JOB_DESCRIPTION_PRESETS } from '../presets';

export default function JobDescriptionSection({ jdText, setJdText }) {
  const wordCount = jdText.trim() ? jdText.trim().split(/\s+/).length : 0;
  const charCount = jdText.length;

  const handleSelectPreset = (preset) => {
    setJdText(preset.text);
  };

  const handleClear = () => {
    setJdText('');
  };

  return (
    <div className="glass-panel jd-card">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-icon-badge">
            <Briefcase size={18} className="text-indigo" />
          </div>
          <div>
            <h2 className="section-title">Target Job Description</h2>
            <p className="section-subtitle">Define role requirements, required competencies, and experience parameters</p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="section-header-actions">
          {jdText && (
            <button
              type="button"
              className="btn-ghost"
              onClick={handleClear}
              title="Clear job description"
            >
              <RotateCcw size={14} />
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* 1-Click Quick Presets */}
      <div className="presets-row">
        <span className="presets-label">
          <Sparkles size={14} className="text-violet" /> Quick Presets:
        </span>
        <div className="presets-chips">
          {JOB_DESCRIPTION_PRESETS.map((p) => {
            const isSelected = jdText === p.text;
            return (
              <button
                key={p.id}
                type="button"
                className={`preset-chip ${isSelected ? 'preset-chip-active' : ''}`}
                onClick={() => handleSelectPreset(p)}
              >
                <span>{p.title}</span>
                <span className="preset-cat-tag">{p.category}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* JD Textarea */}
      <div className="jd-textarea-wrapper">
        <textarea
          className="jd-textarea"
          rows={7}
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
          placeholder="Paste full job description here, or click one of the quick presets above (e.g. Senior Data Scientist, Python Backend Engineer)..."
          id="input-job-description"
        />
        <div className="jd-stats-bar">
          <span className="jd-stat-item">
            <FileText size={13} /> {wordCount} words
          </span>
          <span className="jd-stat-divider">•</span>
          <span className="jd-stat-item">{charCount} characters</span>
          {wordCount >= 50 && (
            <span className="pill pill-success jd-quality-pill">
              Optimal Depth
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
