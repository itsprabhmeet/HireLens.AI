import React, { useState } from 'react';
import { Check, X, Layers, Filter, CheckCircle2, AlertCircle } from 'lucide-react';

export default function SkillsMatrix({
  categorizedSkills = {},
  matchedKeywords = [],
  missingKeywords = [],
}) {
  const [filterMode, setFilterMode] = useState('all'); // 'all' | 'matched' | 'missing'

  const categories = Object.keys(categorizedSkills || {});
  const totalMatched = matchedKeywords.length;
  const totalMissing = missingKeywords.length;
  const totalSkills = totalMatched + totalMissing;
  const coveragePercent = totalSkills > 0 ? Math.round((totalMatched / totalSkills) * 100) : 0;

  return (
    <div className="glass-panel skills-matrix-card">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-icon-badge">
            <Layers size={18} className="text-cyan" />
          </div>
          <div>
            <h2 className="section-title">Categorized Competencies Matrix</h2>
            <p className="section-subtitle">
              Taxonomy classification of matched technical proficiencies vs unaddressed requirements
            </p>
          </div>
        </div>

        {/* Filter controls */}
        <div className="skills-filter-group">
          <button
            type="button"
            className={`filter-btn ${filterMode === 'all' ? 'filter-btn-active' : ''}`}
            onClick={() => setFilterMode('all')}
          >
            All Skills ({totalSkills})
          </button>
          <button
            type="button"
            className={`filter-btn ${filterMode === 'matched' ? 'filter-btn-active' : ''}`}
            onClick={() => setFilterMode('matched')}
          >
            <Check size={13} className="text-emerald" /> Matched ({totalMatched})
          </button>
          <button
            type="button"
            className={`filter-btn ${filterMode === 'missing' ? 'filter-btn-active' : ''}`}
            onClick={() => setFilterMode('missing')}
          >
            <X size={13} className="text-warning" /> Missing ({totalMissing})
          </button>
        </div>
      </div>

      {/* Coverage Banner */}
      <div className="skills-coverage-banner">
        <div className="coverage-info">
          <span className="coverage-label">Overall Skill Coverage:</span>
          <span className="coverage-number">{coveragePercent}%</span>
          <span className="coverage-detail">({totalMatched} of {totalSkills} required competencies)</span>
        </div>
        <div className="coverage-bar">
          <div className="coverage-bar-fill" style={{ width: `${coveragePercent}%` }} />
        </div>
      </div>

      {/* Categorized Grid */}
      {categories.length > 0 ? (
        <div className="categories-grid">
          {categories.map((catName) => {
            const group = categorizedSkills[catName] || {};
            const matched = group.matched || [];
            const missing = group.missing || [];
            const catTotal = matched.length + missing.length;
            const catPercent = catTotal > 0 ? Math.round((matched.length / catTotal) * 100) : 0;

            if (catTotal === 0) return null;
            if (filterMode === 'matched' && matched.length === 0) return null;
            if (filterMode === 'missing' && missing.length === 0) return null;

            return (
              <div key={catName} className="category-card">
                <div className="category-card-header">
                  <div className="category-title-row">
                    <span className="category-name">{catName}</span>
                    <span className="category-score-badge">
                      {matched.length}/{catTotal}
                    </span>
                  </div>
                  <div className="category-progress-track">
                    <div
                      className="category-progress-fill"
                      style={{ width: `${catPercent}%` }}
                    />
                  </div>
                </div>

                <div className="category-chips-flow">
                  {/* Matched Chips */}
                  {(filterMode === 'all' || filterMode === 'matched') &&
                    matched.map((skill, sIdx) => {
                      const skillName = Array.isArray(skill) ? skill[0] : (typeof skill === 'object' && skill !== null ? (skill.name || skill.skill || '') : String(skill));
                      return (
                        <span key={`m-${sIdx}`} className="skill-chip skill-chip-matched">
                          <CheckCircle2 size={13} />
                          <span>{skillName}</span>
                        </span>
                      );
                    })}

                  {/* Missing Chips */}
                  {(filterMode === 'all' || filterMode === 'missing') &&
                    missing.map((skill, sIdx) => {
                      const skillName = Array.isArray(skill) ? skill[0] : (typeof skill === 'object' && skill !== null ? (skill.name || skill.skill || '') : String(skill));
                      return (
                        <span key={`x-${sIdx}`} className="skill-chip skill-chip-missing">
                          <AlertCircle size={13} />
                          <span>{skillName}</span>
                        </span>
                      );
                    })}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Fallback if categorized_skills was empty, render raw matched / missing lists */
        <div className="raw-skills-grid">
          <div className="raw-skills-col">
            <h4 className="raw-col-title text-emerald">Matched Keywords ({totalMatched})</h4>
            <div className="category-chips-flow">
              {matchedKeywords.map((item, idx) => {
                const name = Array.isArray(item) ? item[0] : item;
                return (
                  <span key={idx} className="skill-chip skill-chip-matched">
                    <CheckCircle2 size={13} /> {name}
                  </span>
                );
              })}
            </div>
          </div>
          <div className="raw-skills-col">
            <h4 className="raw-col-title text-warning">Missing Requirements ({totalMissing})</h4>
            <div className="category-chips-flow">
              {missingKeywords.map((item, idx) => {
                const name = Array.isArray(item) ? item[0] : item;
                return (
                  <span key={idx} className="skill-chip skill-chip-missing">
                    <AlertCircle size={13} /> {name}
                  </span>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
