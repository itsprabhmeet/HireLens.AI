import React, { useState } from 'react';
import { RotateCcw, FileText, Link2, Loader2, CheckCircle2, AlertTriangle } from 'lucide-react';
import { JOB_DESCRIPTION_PRESETS } from '../presets';

export default function JobDescriptionSection({ jdText, setJdText }) {
  const wordCount = jdText.trim() ? jdText.trim().split(/\s+/).length : 0;
  const charCount = jdText.length;

  const [showUrlImport, setShowUrlImport] = useState(false);
  const [jobUrl, setJobUrl] = useState('');
  const [fetchingUrl, setFetchingUrl] = useState(false);
  const [fetchMessage, setFetchMessage] = useState(null);

  const handleSelectPreset = (preset) => {
    setJdText(preset.text);
  };

  const handleClear = () => {
    setJdText('');
    setFetchMessage(null);
  };

  const handleFetchUrl = async () => {
    if (!jobUrl.trim()) {
      setFetchMessage({ type: 'error', text: 'Please enter a valid job URL first.' });
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
        setFetchMessage({ type: 'success', text: data.message || 'Job description extracted successfully.' });
      } else {
        setFetchMessage({ type: 'error', text: data.message || 'Could not parse job description from URL.' });
      }
    } catch (err) {
      setFetchMessage({
        type: 'error',
        text: 'Connection failed. Please paste the job description directly.',
      });
    } finally {
      setFetchingUrl(false);
    }
  };

  return (
    <div className="glass-panel jd-card">
      <div className="section-header">
        <div className="section-title-group">
          <div>
            <h2 className="section-title">Job description</h2>
            <p className="section-subtitle">Paste the role you're hiring for, or start from a template</p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="section-header-actions">
          <button
            type="button"
            className={`btn-action-pill ${showUrlImport ? 'btn-action-pill-active' : ''}`}
            onClick={() => setShowUrlImport(!showUrlImport)}
            title="Import job description from a careers page URL"
          >
            <Link2 size={13} />
            <span>Import URL</span>
          </button>
          {jdText && (
            <button
              type="button"
              className="btn-action-pill"
              onClick={handleClear}
              title="Clear job description"
            >
              <RotateCcw size={13} />
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* Collapsible URL Import Drawer */}
      {showUrlImport && (
        <div className="url-import-panel animate-fade-in">
          <div className="url-input-group">
            <Link2 size={14} className="url-input-icon text-muted" />
            <input
              type="text"
              value={jobUrl}
              onChange={(e) => setJobUrl(e.target.value)}
              placeholder="Paste careers URL (e.g. Greenhouse, Lever, LinkedIn, Workday)..."
              id="input-job-url"
              className="url-text-input"
            />
            <button
              type="button"
              className="btn-fetch-submit"
              onClick={handleFetchUrl}
              disabled={fetchingUrl}
            >
              {fetchingUrl ? <Loader2 size={13} className="spinner-icon" /> : null}
              <span>{fetchingUrl ? 'Fetching...' : 'Extract'}</span>
            </button>
          </div>
          {fetchMessage && (
            <div className={`url-feedback ${fetchMessage.type === 'success' ? 'url-feedback-success' : 'url-feedback-error'}`}>
              {fetchMessage.type === 'success' ? <CheckCircle2 size={13} /> : <AlertTriangle size={13} />}
              <span>{fetchMessage.text}</span>
            </div>
          )}
        </div>
      )}

      {/* Role Templates Bar */}
      <div className="role-templates-container">
        <span className="role-templates-label">Templates:</span>
        <div className="role-templates-list">
          {JOB_DESCRIPTION_PRESETS.map((p) => {
            const isSelected = jdText === p.text;
            const shortTitle = p.title.split(' & ')[0].split(' / ')[0];
            return (
              <button
                key={p.id}
                type="button"
                className={`role-template-chip ${isSelected ? 'role-template-chip-active' : ''}`}
                onClick={() => handleSelectPreset(p)}
              >
                <span>{shortTitle}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* JD Textarea */}
      <div className="jd-textarea-wrapper">
        <textarea
          className="jd-textarea"
          rows={9}
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
          placeholder="Paste job description text here, or select a role template above..."
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
              Good detail
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
