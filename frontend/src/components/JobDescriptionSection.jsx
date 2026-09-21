import React, { useState } from 'react';
import { Briefcase, Sparkles, RotateCcw, FileText, Link2, Loader2, CheckCircle2, AlertTriangle } from 'lucide-react';
import { JOB_DESCRIPTION_PRESETS } from '../presets';

export default function JobDescriptionSection({ jdText, setJdText }) {
  const wordCount = jdText.trim() ? jdText.trim().split(/\s+/).length : 0;
  const charCount = jdText.length;

  const [jobUrl, setJobUrl] = useState('');
  const [fetchingUrl, setFetchingUrl] = useState(false);
  const [fetchMessage, setFetchMessage] = useState(null); // { type: 'success' | 'error', text }

  const handleSelectPreset = (preset) => {
    setJdText(preset.text);
  };

  const handleClear = () => {
    setJdText('');
  };

  const handleFetchUrl = async () => {
    if (!jobUrl.trim()) {
      setFetchMessage({ type: 'error', text: 'Paste a job posting URL first.' });
      return;
    }
    setFetchingUrl(true);
    setFetchMessage(null);
    try {
      const response = await fetch('/api/fetch-job-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: jobUrl }),
      });
      const data = await response.json();
      if (data.success) {
        setJdText(data.text);
        setFetchMessage({ type: 'success', text: data.message });
      } else {
        setFetchMessage({ type: 'error', text: data.message });
      }
    } catch (err) {
      setFetchMessage({
        type: 'error',
        text: 'Could not reach the server to fetch that link. Please paste the job description text instead.',
      });
    } finally {
      setFetchingUrl(false);
    }
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

      {/* Paste a job link instead of typing */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '10px' }}>
        <div style={{
          flex: 1, display: 'flex', alignItems: 'center', gap: '8px',
          background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '10px', padding: '0 12px',
        }}>
          <Link2 size={15} className="text-indigo" style={{ flexShrink: 0, opacity: 0.7 }} />
          <input
            type="text"
            value={jobUrl}
            onChange={(e) => setJobUrl(e.target.value)}
            placeholder="Or paste a job posting link (e.g. a company careers page)..."
            id="input-job-url"
            style={{
              flex: 1, background: 'transparent', border: 'none', outline: 'none',
              color: 'inherit', padding: '10px 0', fontSize: '0.9rem',
            }}
          />
        </div>
        <button
          type="button"
          className="btn-ghost"
          onClick={handleFetchUrl}
          disabled={fetchingUrl}
        >
          {fetchingUrl ? <Loader2 size={14} /> : <Link2 size={14} />}
          <span>{fetchingUrl ? 'Fetching...' : 'Fetch'}</span>
        </button>
      </div>
      {fetchMessage && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem',
          marginBottom: '14px',
        }} className={fetchMessage.type === 'success' ? 'text-emerald' : 'text-warning'}>
          {fetchMessage.type === 'success' ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
          <span>{fetchMessage.text}</span>
        </div>
      )}

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
