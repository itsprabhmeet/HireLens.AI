import React from 'react';
import { Target, Award, Brain, Zap, ShieldCheck } from 'lucide-react';

export default function ScoreGauge({
  fitScore = 0,
  predictedCategory = '',
  semanticSimilarity = 0,
  lexicalRelevance = 0,
  categoryAlignment = 0,
  confidence = 0,
  blindMode = false,
  redactionCounts = null,
}) {
  const score = Math.min(100, Math.max(0, Math.round(fitScore * 10) / 10));

  // Determine score tier & colors
  let tierLabel = 'Low Match';
  let tierPillClass = 'pill-danger';
  let strokeClass = 'gauge-progress-danger';

  if (score >= 75) {
    tierLabel = 'Strong Match';
    tierPillClass = 'pill-success';
    strokeClass = 'gauge-progress-success';
  } else if (score >= 50) {
    tierLabel = 'Potential Match';
    tierPillClass = 'pill-warning';
    strokeClass = 'gauge-progress-warning';
  }

  // Normalize subscore percentages (handles both 0-1 ratio and already scaled 0-100 values)
  const normalizePercent = (val) => {
    const num = Number(val) || 0;
    const pct = num > 1.0 ? num : num * 100;
    return Math.min(100, Math.max(0, Math.round(pct * 10) / 10));
  };

  const semPct = normalizePercent(semanticSimilarity);
  const lexPct = normalizePercent(lexicalRelevance);
  const catPct = normalizePercent(categoryAlignment);

  // SVG Circular Gauge calculation
  const radius = 80;
  const strokeWidth = 12;
  const circumference = 2 * Math.PI * radius;
  // Let's use a 260 degree arc or full 360 ring
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="glass-panel score-gauge-panel">
      <div className="gauge-main-col">
        {/* Radial SVG Gauge */}
        <div className="svg-gauge-container">
          <svg className="svg-gauge" width="200" height="200" viewBox="0 0 200 200">
            {/* Background Track Ring */}
            <circle
              className="gauge-track"
              cx="100"
              cy="100"
              r={radius}
              strokeWidth={strokeWidth}
              fill="transparent"
            />

            {/* Value Progress Ring */}
            <circle
              className={`gauge-progress ${strokeClass}`}
              cx="100"
              cy="100"
              r={radius}
              strokeWidth={strokeWidth}
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              transform="rotate(-90 100 100)"
            />
          </svg>

          {/* Center Text */}
          <div className="gauge-center-content">
            <span className="gauge-score-number">{score}%</span>
            <span className={`pill ${tierPillClass} gauge-tier-pill`}>{tierLabel}</span>
            <span className="gauge-score-caption">Fit Index</span>
          </div>
        </div>

        {/* Predicted Domain Alignment */}
        {predictedCategory && (
          <div className="predicted-category-block">
            <span className="pred-label">ML Predicted Role:</span>
            <span className="pill pill-brand pred-category-pill">
              <Brain size={13} /> {predictedCategory}
              {confidence > 0 && <span className="pred-confidence"> ({confidence}%)</span>}
            </span>
          </div>
        )}

        {/* Blind Mode Audit Badge */}
        {blindMode && redactionCounts && (
          <div className="blind-audit-card">
            <div className="blind-audit-header">
              <ShieldCheck size={14} className="text-emerald" />
              <span>Bias Redaction Active</span>
            </div>
            <div className="blind-redaction-counts">
              {redactionCounts.names > 0 && <span>{redactionCounts.names} Name(s)</span>}
              {redactionCounts.emails > 0 && <span>{redactionCounts.emails} Email(s)</span>}
              {redactionCounts.phones > 0 && <span>{redactionCounts.phones} Phone(s)</span>}
              {redactionCounts.links > 0 && <span>{redactionCounts.links} Link(s)</span>}
            </div>
          </div>
        )}
      </div>

      {/* Sub-Score Breakdown Pillars */}
      <div className="gauge-subscores-col">
        <h3 className="subscores-heading">
          <Target size={16} className="text-indigo" />
          <span>Multimodal Scoring Vectors</span>
        </h3>

        {/* Semantic Similarity */}
        <div className="subscore-card">
          <div className="subscore-row">
            <div className="subscore-info">
              <Zap size={15} className="text-cyan" />
              <span className="subscore-title">Semantic Context Match</span>
            </div>
            <span className="subscore-value">{semPct}%</span>
          </div>
          <div className="subscore-progress-bar">
            <div
              className="subscore-progress-fill fill-cyan"
              style={{ width: `${semPct}%` }}
            />
          </div>
          <span className="subscore-note">Neural embeddings capturing underlying conceptual alignment</span>
        </div>

        {/* Lexical Keyword Overlap */}
        <div className="subscore-card">
          <div className="subscore-row">
            <div className="subscore-info">
              <Award size={15} className="text-emerald" />
              <span className="subscore-title">Keyword & Skill Density</span>
            </div>
            <span className="subscore-value">{lexPct}%</span>
          </div>
          <div className="subscore-progress-bar">
            <div
              className="subscore-progress-fill fill-emerald"
              style={{ width: `${lexPct}%` }}
            />
          </div>
          <span className="subscore-note">Exact keyword & technical vocabulary overlap with role JD</span>
        </div>

        {/* ML Model Alignment */}
        <div className="subscore-card">
          <div className="subscore-row">
            <div className="subscore-info">
              <Brain size={15} className="text-violet" />
              <span className="subscore-title">Domain Experience Alignment</span>
            </div>
            <span className="subscore-value">{catPct}%</span>
          </div>
          <div className="subscore-progress-bar">
            <div
              className="subscore-progress-fill fill-violet"
              style={{ width: `${catPct}%` }}
            />
          </div>
          <span className="subscore-note">Classifier probability that candidate's profile matches target job domain</span>
        </div>
      </div>
    </div>
  );
}
