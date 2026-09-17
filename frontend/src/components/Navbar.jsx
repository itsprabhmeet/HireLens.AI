import React from 'react';
import { Sparkles, Users, UserCheck, ShieldCheck, EyeOff, Activity, Cpu } from 'lucide-react';

export default function Navbar({
  mode,
  setMode,
  blindMode,
  setBlindMode,
  backendStatus,
}) {
  return (
    <header className="navbar-container">
      <div className="navbar-inner">
        {/* Brand Logo & Name */}
        <div className="navbar-brand">
          <div className="brand-icon-wrapper">
            <Sparkles className="brand-icon" size={22} />
          </div>
          <div className="brand-text-block">
            <div className="brand-title-row">
              <span className="brand-title">HireLens<span className="brand-dot">.AI</span></span>
              <span className="pill pill-brand brand-badge">
                <Cpu size={12} /> v2.0 PRO
              </span>
            </div>
            <span className="brand-subtitle">Explainable Talent Intelligence & Job-Fit Classifier</span>
          </div>
        </div>

        {/* Mode Switcher Segmented Control */}
        <div className="navbar-mode-switch">
          <button
            type="button"
            className={`mode-tab ${mode === 'single' ? 'mode-tab-active' : ''}`}
            onClick={() => setMode('single')}
            id="tab-single-screening"
          >
            <UserCheck size={16} />
            <span>Single Deep-Dive</span>
          </button>
          <button
            type="button"
            className={`mode-tab ${mode === 'batch' ? 'mode-tab-active' : ''}`}
            onClick={() => setMode('batch')}
            id="tab-batch-screening"
          >
            <Users size={16} />
            <span>Batch Leaderboard</span>
          </button>
        </div>

        {/* Right Controls: Blind Mode Toggle & System Status */}
        <div className="navbar-actions">
          {/* Blind Mode Toggle */}
          <div
            className={`blind-mode-toggle ${blindMode ? 'blind-mode-active' : ''}`}
            onClick={() => setBlindMode(!blindMode)}
            title="Anonymize candidate names, emails, phones, and links to ensure 100% merit-based evaluation without unconscious bias."
            role="button"
            tabIndex={0}
            id="toggle-blind-mode"
          >
            {blindMode ? (
              <ShieldCheck size={17} className="text-emerald" />
            ) : (
              <EyeOff size={17} className="text-secondary" />
            )}
            <div className="blind-toggle-label">
              <span className="blind-title">Blind Mode</span>
              <span className="blind-sub">{blindMode ? 'Active (Bias-Free)' : 'Off'}</span>
            </div>
            <div className={`switch-pill ${blindMode ? 'switch-on' : ''}`}>
              <div className="switch-thumb" />
            </div>
          </div>

          {/* Engine Status */}
          <div className="server-status-pill" title={backendStatus ? 'Connected to FastAPI AI Engine' : 'Checking server status...'}>
            <span className={`status-dot ${backendStatus ? 'status-dot-online' : 'status-dot-offline'}`} />
            <span className="status-label">{backendStatus ? 'Engine Ready' : 'Connecting...'}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
