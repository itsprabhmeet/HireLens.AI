import React from 'react';
import { Target, Users, UserCheck, ShieldCheck, EyeOff, CheckCircle2 } from 'lucide-react';

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
        {/* Brand Logo */}
        <div className="navbar-brand">
          <div className="brand-logo-mark">
            <Target size={18} className="brand-logo-icon" />
          </div>
          <div className="brand-text-block">
            <div className="brand-title-row">
              <span className="brand-title">HireLens</span>
            </div>
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
            <UserCheck size={15} />
            <span>Single Evaluation</span>
          </button>
          <button
            type="button"
            className={`mode-tab ${mode === 'batch' ? 'mode-tab-active' : ''}`}
            onClick={() => setMode('batch')}
            id="tab-batch-screening"
          >
            <Users size={15} />
            <span>Batch Leaderboard</span>
          </button>
        </div>

        {/* Right Controls: Blind Mode Toggle & System Status */}
        <div className="navbar-actions">
          {/* Blind Mode Toggle */}
          <div
            className={`blind-mode-toggle ${blindMode ? 'blind-mode-active' : ''}`}
            onClick={() => setBlindMode(!blindMode)}
            title="Hide candidate names, emails, phones, and profile links while scoring"
            role="button"
            tabIndex={0}
            id="toggle-blind-mode"
          >
            {blindMode ? (
              <ShieldCheck size={16} className="text-emerald" />
            ) : (
              <EyeOff size={16} className="text-muted" />
            )}
            <div className="blind-toggle-label">
              <span className="blind-title">Blind Mode</span>
              <span className="blind-sub">{blindMode ? 'Anonymized' : 'Standard'}</span>
            </div>
            <div className={`switch-pill ${blindMode ? 'switch-on' : ''}`}>
              <div className="switch-thumb" />
            </div>
          </div>

        </div>
      </div>
    </header>
  );
}
