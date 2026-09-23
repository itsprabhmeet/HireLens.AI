import React from 'react';
import { HelpCircle } from 'lucide-react';

export default function ShapVisualizer({ shapFeatures = {} }) {
  const entries = Object.entries(shapFeatures || {});
  
  if (entries.length === 0) {
    return null;
  }

  // Find max absolute value to scale bars relative to 100%
  const maxAbsVal = Math.max(...entries.map(([, val]) => Math.abs(val)), 0.001);

  // Sort descending by magnitude or signed value
  const sortedEntries = [...entries].sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));

  return (
    <div className="glass-panel shap-visualizer-card">
      <div className="section-header">
        <div className="section-title-group">
          <div>
            <h2 className="section-title">Why this score</h2>
            <p className="section-subtitle">
              The terms that pushed the score up or down the most
            </p>
          </div>
        </div>

        <div className="shap-legend">
          <span className="legend-item">
            <span className="legend-box bg-emerald" /> Helped
          </span>
          <span className="legend-item">
            <span className="legend-box bg-danger" /> Hurt
          </span>
        </div>
      </div>

      <div className="shap-bars-container">
        {sortedEntries.slice(0, 10).map(([featureName, rawVal], idx) => {
          const val = Number(rawVal);
          const isPositive = val >= 0;
          const barWidthPercent = Math.min(100, Math.round((Math.abs(val) / maxAbsVal) * 90) + 10);

          return (
            <div key={idx} className="shap-bar-row">
              <div className="shap-feature-col">
                <span className="shap-feature-name" title={featureName}>
                  {featureName}
                </span>
              </div>

              <div className="shap-diverging-track">
                {/* Center baseline divider */}
                <div className="shap-center-axis" />

                {/* Left side: Negative impact */}
                <div className="shap-negative-half">
                  {!isPositive && (
                    <div
                      className="shap-bar shap-bar-negative"
                      style={{ width: `${barWidthPercent}%` }}
                    >
                      <span className="shap-val-text">{val.toFixed(3)}</span>
                    </div>
                  )}
                </div>

                {/* Right side: Positive impact */}
                <div className="shap-positive-half">
                  {isPositive && (
                    <div
                      className="shap-bar shap-bar-positive"
                      style={{ width: `${barWidthPercent}%` }}
                    >
                      <span className="shap-val-text">+{val.toFixed(3)}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="shap-footnote">
        <HelpCircle size={14} className="text-muted" />
        <span>
          Green bars are terms in the resume that match the role. Red bars are expected terms that were missing.
        </span>
      </div>
    </div>
  );
}
