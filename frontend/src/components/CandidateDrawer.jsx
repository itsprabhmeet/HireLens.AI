import React, { useEffect } from 'react';
import { X, FileText, ExternalLink, ShieldCheck } from 'lucide-react';
import ScoreGauge from './ScoreGauge';
import NarrativeCard from './NarrativeCard';
import SkillsMatrix from './SkillsMatrix';
import ShapVisualizer from './ShapVisualizer';
import InterviewQuestionsCard from './InterviewQuestionsCard';

export default function CandidateDrawer({
  candidate,
  onClose,
  onOpenRawResume,
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!candidate) return null;

  const score = Math.round(candidate.fit_score * 10) / 10;
  let tierPill = 'pill-danger';
  let tierLabel = 'Low Match';
  if (score >= 75) {
    tierPill = 'pill-success';
    tierLabel = 'Strong Match';
  } else if (score >= 50) {
    tierPill = 'pill-warning';
    tierLabel = 'Potential Match';
  }

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div
        className="drawer-container"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div className="drawer-header">
          <div className="drawer-header-left">
            <div className="drawer-title-row">
              <h2 className="drawer-candidate-name">{candidate.candidate}</h2>
              <span className={`pill ${tierPill}`}>{tierLabel}</span>
            </div>
            <div className="drawer-meta-row">
              <span className="drawer-filename">
                <FileText size={13} /> {candidate.filename}
              </span>
              {candidate.redaction_counts && candidate.redaction_counts.names > 0 && (
                <span className="pill pill-neutral">
                  <ShieldCheck size={12} className="text-emerald" /> Blind Screened
                </span>
              )}
            </div>
          </div>

          <div className="drawer-header-right">
            {candidate.raw_text && (
              <button
                type="button"
                className="btn-secondary drawer-btn-raw"
                onClick={() => onOpenRawResume(candidate)}
              >
                <ExternalLink size={14} />
                <span>View Resume</span>
              </button>
            )}
            <button
              type="button"
              className="drawer-btn-close"
              onClick={onClose}
              title="Close drawer"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Drawer Scrollable Content */}
        <div className="drawer-body">
          {/* Score & Subscore Gauges */}
          <ScoreGauge
            fitScore={candidate.fit_score}
            predictedCategory={candidate.predicted_category}
            semanticSimilarity={candidate.semantic_similarity}
            lexicalRelevance={candidate.lexical_relevance || candidate.jd_relevance}
            categoryAlignment={candidate.category_alignment}
            confidence={candidate.confidence}
            blindMode={candidate.redaction_counts && candidate.redaction_counts.names > 0}
            redactionCounts={candidate.redaction_counts}
          />

          {/* AI Narrative Synthesis */}
          <NarrativeCard narrative={candidate.narrative} />

          {/* Categorized Skills Breakdown */}
          <SkillsMatrix
            categorizedSkills={candidate.categorized_skills}
            matchedKeywords={candidate.matched_keywords}
            missingKeywords={candidate.missing_keywords}
          />

          {/* Targeted Interview Questions */}
          {candidate.narrative && candidate.narrative.interview_questions && (
            <InterviewQuestionsCard
              questions={candidate.narrative.interview_questions}
            />
          )}

          {/* SHAP Feature Importance */}
          {candidate.shap_features && Object.keys(candidate.shap_features).length > 0 && (
            <ShapVisualizer shapFeatures={candidate.shap_features} />
          )}
        </div>
      </div>
    </div>
  );
}
