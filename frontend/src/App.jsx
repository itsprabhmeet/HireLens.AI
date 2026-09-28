import React, { useState, useEffect, useCallback } from 'react';
import {
  AlertTriangle,
  Loader2,
  CheckCircle2,
  Zap,
  BarChart2,
  Shield,
  FileCheck,
} from 'lucide-react';

import Navbar from './components/Navbar';
import JobDescriptionSection from './components/JobDescriptionSection';
import ResumeUpload from './components/ResumeUpload';
import ScoreGauge from './components/ScoreGauge';
import NarrativeCard from './components/NarrativeCard';
import SkillsMatrix from './components/SkillsMatrix';
import LearningRecommendations from './components/LearningRecommendations';
import ShapVisualizer from './components/ShapVisualizer';
import InterviewQuestionsCard from './components/InterviewQuestionsCard';
import LeaderboardTable from './components/LeaderboardTable';
import CandidateDrawer from './components/CandidateDrawer';
import ResumeInspectorModal from './components/ResumeInspectorModal';
import EvaluationLoader from './components/EvaluationLoader';

import { JOB_DESCRIPTION_PRESETS } from './presets';

const SINGLE_STAGES = [
  'Reading resume and identifying skills...',
  'Comparing against the job description...',
  'Putting together the summary...',
];

export default function App() {
  // Navigation & Settings
  const [mode, setMode] = useState('single'); // 'single' | 'batch'
  const [blindMode, setBlindMode] = useState(false);
  const [backendStatus, setBackendStatus] = useState(false);
  const [backendChecked, setBackendChecked] = useState(false);

  // Theme (light/dark) — initial value is set synchronously in index.html to avoid a flash
  const [theme, setTheme] = useState(() => {
    if (typeof document !== 'undefined') {
      const current = document.documentElement.getAttribute('data-theme');
      if (current === 'light' || current === 'dark') return current;
    }
    return 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('hirelens-theme', theme);
    } catch {
      // ignore
    }
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'));

  // Job Description state (prefill with realistic Data Science JD)
  const [jdText, setJdText] = useState(JOB_DESCRIPTION_PRESETS[0].text);

  // Single Screening input state
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeText, setResumeText] = useState('');

  // Batch Screening input state
  const [batchFiles, setBatchFiles] = useState([]);

  // Results State
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const [error, setError] = useState(null);
  const [evalResult, setEvalResult] = useState(null);
  const [batchResults, setBatchResults] = useState(null);

  // Modal / Drawer state
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [rawResumeCandidate, setRawResumeCandidate] = useState(null);

  // Check backend health on mount
  useEffect(() => {
    let active = true;
    async function checkHealth() {
      try {
        const res = await fetch('/api/status');
        if (res.ok) {
          const data = await res.json();
          if (active) setBackendStatus(data.status === 'ready');
        } else {
          if (active) setBackendStatus(false);
        }
      } catch {
        if (active) setBackendStatus(false);
      } finally {
        if (active) setBackendChecked(true);
      }
    }
    checkHealth();
    return () => {
      active = false;
    };
  }, []);

  // Single resume evaluation
  const handleScreenSingle = useCallback(async () => {
    if (loading) return;
    if (!jdText.trim()) {
      setError('Please provide a job description before evaluating.');
      return;
    }
    if (!resumeFile && !resumeText.trim()) {
      setError('Please upload a resume file or paste resume content to evaluate.');
      return;
    }

    setError(null);
    setLoading(true);
    setLoadingStage(SINGLE_STAGES[0]);

    const stageTimer1 = setTimeout(() => {
      setLoadingStage(SINGLE_STAGES[1]);
    }, 1100);

    const stageTimer2 = setTimeout(() => {
      setLoadingStage(SINGLE_STAGES[2]);
    }, 2200);

    try {
      const formData = new FormData();
      formData.append('jd_text', jdText);
      formData.append('blind_mode', blindMode);

      if (resumeFile) {
        formData.append('file', resumeFile);
      } else {
        formData.append('resume_text', resumeText);
      }

      const response = await fetch('/api/screen', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Evaluation failed' }));
        throw new Error(errData.detail || `Server responded with status ${response.status}`);
      }

      const data = await response.json();
      setEvalResult(data);

      // Smooth scroll to results
      setTimeout(() => {
        const el = document.getElementById('evaluation-results-anchor');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 150);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred during evaluation.');
    } finally {
      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);
      setLoading(false);
      setLoadingStage('');
    }
  }, [loading, jdText, resumeFile, resumeText, blindMode]);

  // Batch resumes evaluation
  const handleScreenBatch = useCallback(async () => {
    if (loading) return;
    if (!jdText.trim()) {
      setError('Please provide a target job description before batch screening.');
      return;
    }
    if (batchFiles.length === 0) {
      setError('Please upload at least one candidate resume for batch screening.');
      return;
    }

    setError(null);
    setLoading(true);
    setLoadingStage(`Evaluating and ranking ${batchFiles.length} candidate resumes...`);

    try {
      const formData = new FormData();
      formData.append('jd_text', jdText);
      formData.append('blind_mode', blindMode);

      batchFiles.forEach((file) => {
        formData.append('files', file);
      });

      const response = await fetch('/api/batch-screen', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Batch screening failed' }));
        throw new Error(errData.detail || `Server responded with status ${response.status}`);
      }

      const data = await response.json();
      setBatchResults(data.candidates || data.leaderboard || []);

      setTimeout(() => {
        const el = document.getElementById('batch-leaderboard-anchor');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 150);
    } catch (err) {
      setError(err.message || 'Batch screening encountered an error.');
    } finally {
      setLoading(false);
      setLoadingStage('');
    }
  }, [loading, jdText, batchFiles, blindMode]);

  // Keyboard shortcut: Ctrl+Enter or Cmd+Enter to run screening
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (mode === 'single') {
          handleScreenSingle();
        } else {
          handleScreenBatch();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [mode, handleScreenSingle, handleScreenBatch]);

  const hasSingleInput = Boolean(resumeFile || resumeText.trim());
  const hasBatchInput = batchFiles.length > 0;
  const isReadyToRun = mode === 'single' ? hasSingleInput : hasBatchInput;

  if (!backendChecked) {
    return (
      <div className="engine-boot-screen">
        <div className="engine-boot-icon-wrapper">
          <Loader2 size={28} className="engine-boot-spinner" color="#ffffff" />
        </div>
        <div className="engine-boot-title">Waking up the engine...</div>
        <div className="engine-boot-subtitle">
          The AI models are loading. This can take up to a minute if the server has been idle.
        </div>
      </div>
    );
  }

  return (
    <div className="app-layout">
      {/* Top Navigation */}
      <Navbar
        mode={mode}
        setMode={setMode}
        blindMode={blindMode}
        setBlindMode={setBlindMode}
        backendStatus={backendStatus}
        backendChecked={backendChecked}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      {/* Workspace Sub-header */}
      <section className="workspace-header">
        <div className="workspace-header-inner">
          <div className="workspace-header-left">
            <div className="workspace-breadcrumb">
              <span className="breadcrumb-root">HireLens</span>
              <span className="breadcrumb-separator">/</span>
              <span className="breadcrumb-current">
                {mode === 'single' ? 'Single candidate' : 'Batch ranking'}
              </span>
            </div>
            <h1 className="workspace-title">
              {mode === 'single' ? 'Candidate match assessment' : 'Batch applicant ranking'}
            </h1>
            <p className="workspace-subtitle">
              {mode === 'single'
                ? 'Compare a resume against a job description to see fit, skill gaps, and what to ask in the interview.'
                : 'Screen a batch of resumes against one job description and rank them side by side.'}
            </p>
          </div>

          {blindMode && (
            <div className="workspace-header-right">
              <div className="workspace-stat-badge stat-badge-blind">
                <Shield size={12} className="text-emerald" />
                <span className="stat-badge-text">Blind mode on</span>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Main Workspace Container */}
      <main className="main-content-container">
        {/* Error Notification Callout */}
        {error && (
          <div className="alert-banner alert-banner-danger animate-fade-in">
            <AlertTriangle size={18} />
            <div className="alert-text-block">
              <span className="alert-title">Evaluation Notice</span>
              <p className="alert-msg">{error}</p>
            </div>
            <button
              type="button"
              className="btn-icon-ghost"
              onClick={() => setError(null)}
            >
              &times;
            </button>
          </div>
        )}

        {/* Top Split Inputs: Job Description & Candidate Resume(s) */}
        <div className="inputs-split-grid">
          {/* Target Job Description */}
          <JobDescriptionSection jdText={jdText} setJdText={setJdText} />

          {/* Candidate Resume Input */}
          <ResumeUpload
            mode={mode}
            resumeFile={resumeFile}
            setResumeFile={setResumeFile}
            resumeText={resumeText}
            setResumeText={setResumeText}
            batchFiles={batchFiles}
            setBatchFiles={setBatchFiles}
          />
        </div>

        {/* Primary Action Dock */}
        <div className="action-dock">
          <div className="action-dock-inner">
            <div className="action-dock-status">
              <div className="dock-status-icon">
                {loading ? (
                  <Loader2 size={16} className="spinner-icon text-indigo" />
                ) : (
                  <Zap size={16} className={isReadyToRun ? 'text-indigo' : 'text-muted'} />
                )}
              </div>
              <div className="dock-status-text-block">
                <span className="dock-status-title">
                  {loading ? (loadingStage || 'Working...') : isReadyToRun ? 'Evaluation staged' : 'Add a resume to continue'}
                </span>
                <span className="dock-status-desc">
                  {mode === 'single'
                    ? (resumeFile ? `Resume file: ${resumeFile.name}` : resumeText.trim() ? `${resumeText.trim().split(/\s+/).length} words entered` : 'Attach a PDF/DOCX resume or paste text above')
                    : (`${batchFiles.length} candidate file(s) staged`)}
                </span>
              </div>
            </div>

            <div className="action-dock-controls">
              <button
                type="button"
                className="btn-primary btn-run-evaluation"
                disabled={loading || !isReadyToRun}
                onClick={mode === 'single' ? handleScreenSingle : handleScreenBatch}
                id="btn-run-screening"
              >
                {loading ? (
                  <>
                    <Loader2 size={16} className="spinner-icon" />
                    <span>Analyzing...</span>
                  </>
                ) : mode === 'single' ? (
                  <>
                    <span>Evaluate Candidate</span>
                    <span className="btn-shortcut-hint">Ctrl ↵</span>
                  </>
                ) : (
                  <>
                    <BarChart2 size={16} />
                    <span>Rank Candidates ({batchFiles.length})</span>
                    <span className="btn-shortcut-hint">Ctrl ↵</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* RESULTS SECTION: SINGLE CANDIDATE DEEP-DIVE */}
        {mode === 'single' && evalResult && (
          <div id="evaluation-results-anchor" className="results-container animate-fade-in">
            <div className="results-header-bar">
              <div className="results-title-group">
                <div className="results-status-icon">
                  <CheckCircle2 size={18} className="text-emerald" />
                </div>
                <div>
                  <h2 className="results-heading">
                    {evalResult.candidate_name || 'Candidate'}
                  </h2>
                  <p className="results-subheading">
                    Predicted role: <strong className="text-primary">{evalResult.predicted_category || 'N/A'}</strong>
                  </p>
                </div>
              </div>

              <div className="results-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setRawResumeCandidate(evalResult)}
                >
                  <FileCheck size={14} />
                  <span>View resume text</span>
                </button>
              </div>
            </div>

            {/* Top Results Grid: Score Gauge + Executive Narrative */}
            <div className="results-top-grid">
              <ScoreGauge
                fitScore={evalResult.fit_score}
                predictedCategory={evalResult.predicted_category}
                semanticSimilarity={evalResult.semantic_similarity}
                lexicalRelevance={evalResult.lexical_relevance}
                categoryAlignment={evalResult.category_alignment}
                confidence={evalResult.confidence}
                blindMode={evalResult.blind_mode}
                redactionCounts={evalResult.redaction_counts}
              />

              <NarrativeCard narrative={evalResult.narrative} />
            </div>

            {/* Skills Competency Matrix */}
            <SkillsMatrix
              categorizedSkills={evalResult.categorized_skills}
              matchedKeywords={evalResult.matched_keywords}
              missingKeywords={evalResult.missing_keywords}
            />

            {/* Targeted Learning & Upskilling Recommendations */}
            <LearningRecommendations
              skillGaps={evalResult.skill_gaps}
              jobRole={evalResult.predicted_category}
            />

            {/* Bottom 2-col: SHAP Explainability & Interview Probes */}
            <div className="results-bottom-grid">
              <ShapVisualizer shapFeatures={evalResult.shap_features} />

              {evalResult.narrative && evalResult.narrative.interview_questions && (
                <InterviewQuestionsCard questions={evalResult.narrative.interview_questions} />
              )}
            </div>
          </div>
        )}

        {/* Analysis-in-progress skeleton (Single mode) */}
        {mode === 'single' && loading && !evalResult && (
          <div className="results-container animate-fade-in">
            <div className="glass-panel skeleton-results">
              <div className="skeleton-score-row">
                <div className="skeleton skeleton-circle" />
                <div>
                  <div className="skeleton skeleton-line skeleton-line-md" />
                  <div className="skeleton skeleton-line skeleton-line-lg" />
                  <div className="skeleton skeleton-line skeleton-line-sm" />
                </div>
              </div>
            </div>
            <div className="glass-panel skeleton-results">
              <div className="skeleton skeleton-line skeleton-line-sm" />
              <div className="skeleton skeleton-line skeleton-line-lg" />
              <div className="skeleton skeleton-line skeleton-line-lg" />
              <div className="skeleton skeleton-line skeleton-line-md" />
            </div>
            <div className="glass-panel skeleton-results">
              <div className="skeleton skeleton-line skeleton-line-sm" />
              <div className="skeleton-chips-row">
                <div className="skeleton skeleton-chip" />
                <div className="skeleton skeleton-chip" />
                <div className="skeleton skeleton-chip" />
                <div className="skeleton skeleton-chip" />
              </div>
            </div>
          </div>
        )}

        {/* RESULTS SECTION: BATCH CANDIDATES LEADERBOARD */}
        {mode === 'batch' && batchResults && (
          <div id="batch-leaderboard-anchor" className="results-container animate-fade-in">
            <LeaderboardTable
              candidates={batchResults}
              blindMode={blindMode}
              onSelectCandidate={(cand) => setSelectedCandidate(cand)}
            />
          </div>
        )}
      </main>

      {/* Slide-over Profile Drawer (Batch inspection) */}
      <CandidateDrawer
        candidate={selectedCandidate}
        onClose={() => setSelectedCandidate(null)}
        onOpenRawResume={(cand) => {
          setSelectedCandidate(null);
          setRawResumeCandidate(cand);
        }}
      />

      {/* Raw Resume Inspector Modal */}
      <ResumeInspectorModal
        candidate={rawResumeCandidate}
        onClose={() => setRawResumeCandidate(null)}
      />

      <EvaluationLoader
        open={loading}
        title={mode === 'single' ? 'Evaluating candidate' : `Ranking ${batchFiles.length} candidates`}
        subtitle={mode === 'single'
          ? (resumeFile ? resumeFile.name : 'Pasted resume text')
          : 'Scoring every resume against the job description'}
        steps={mode === 'single'
          ? SINGLE_STAGES.map((s) => s.replace(/\.\.\.$/, ''))
          : ['Reading resumes', 'Scoring against the job description', 'Building the leaderboard']}
        activeStep={mode === 'single' ? Math.max(0, SINGLE_STAGES.indexOf(loadingStage)) : 1}
      />

      {/* Clean Footer */}
      <footer className="app-footer">
        <div className="footer-inner">
          <div className="footer-left">
            <span className="footer-brand-title">HireLens</span>
            <span className="footer-separator">•</span>
            <span className="footer-copyright">Resume screening & match scoring</span>
          </div>
          <div className="footer-right">
            <span className="footer-author">Built by Prabhmeet Singh</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
