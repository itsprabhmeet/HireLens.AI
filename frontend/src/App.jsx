import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import {
  Sparkles,
  ArrowRight,
  AlertTriangle,
  Loader2,
  CheckCircle2,
  RefreshCw,
  Zap,
  BarChart2,
  Shield,
} from 'lucide-react';

import Navbar from './components/Navbar';
import JobDescriptionSection from './components/JobDescriptionSection';
import ResumeUpload from './components/ResumeUpload';
import ScoreGauge from './components/ScoreGauge';
import NarrativeCard from './components/NarrativeCard';
import SkillsMatrix from './components/SkillsMatrix';
import ShapVisualizer from './components/ShapVisualizer';
import InterviewQuestionsCard from './components/InterviewQuestionsCard';
import LeaderboardTable from './components/LeaderboardTable';
import CandidateDrawer from './components/CandidateDrawer';
import ResumeInspectorModal from './components/ResumeInspectorModal';

import { JOB_DESCRIPTION_PRESETS, RESUME_PRESETS } from './presets';

export default function App() {
  // Navigation & Settings
  const [mode, setMode] = useState('single'); // 'single' | 'batch'
  const [blindMode, setBlindMode] = useState(false);
  const [backendStatus, setBackendStatus] = useState(false);

  // Job Description state (prefill with realistic Data Science JD for zero-friction demo)
  const [jdText, setJdText] = useState(JOB_DESCRIPTION_PRESETS[0].text);

  // Single Screening input state
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeText, setResumeText] = useState(RESUME_PRESETS[0].text);

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
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const res = await fetch('/api/status');
      if (res.ok) {
        const data = await res.json();
        setBackendStatus(data.status === 'ready');
      } else {
        setBackendStatus(false);
      }
    } catch {
      setBackendStatus(false);
    }
  };

  // Trigger celebratory confetti for strong candidates
  const fireConfetti = () => {
    try {
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#6366f1', '#a855f7', '#10b981', '#38bdf8'],
      });
    } catch {
      // ignore
    }
  };

  // Single resume evaluation
  const handleScreenSingle = async () => {
    if (!jdText.trim()) {
      setError('Please provide a target job description before screening.');
      return;
    }
    if (!resumeFile && !resumeText.trim()) {
      setError('Please upload a resume or paste resume text to evaluate.');
      return;
    }

    setError(null);
    setLoading(true);
    setLoadingStage('Extracting text & parsing skills...');

    const stageTimer1 = setTimeout(() => {
      setLoadingStage('Generating neural embeddings & semantic similarity...');
    }, 1200);

    const stageTimer2 = setTimeout(() => {
      setLoadingStage('Synthesizing recruiter narrative & interview probes...');
    }, 2500);

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
        const errData = await response.json().catch(() => ({ detail: 'Screening failed' }));
        throw new Error(errData.detail || `Server responded with status ${response.status}`);
      }

      const data = await response.json();
      setEvalResult(data);

      if (data.fit_score >= 70) {
        fireConfetti();
      }

      // Smooth scroll to results
      setTimeout(() => {
        const el = document.getElementById('evaluation-results-anchor');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 150);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred during screening.');
    } finally {
      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);
      setLoading(false);
      setLoadingStage('');
    }
  };

  // Batch resumes evaluation
  const handleScreenBatch = async () => {
    if (!jdText.trim()) {
      setError('Please provide a target job description before batch screening.');
      return;
    }
    if (batchFiles.length === 0) {
      setError('Please upload or load at least one resume for batch screening.');
      return;
    }

    setError(null);
    setLoading(true);
    setLoadingStage(`Evaluating and benchmarking ${batchFiles.length} candidates in parallel...`);

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
      setBatchResults(data.candidates || []);

      if (data.candidates && data.candidates.some((c) => c.fit_score >= 75)) {
        fireConfetti();
      }

      // Smooth scroll to leaderboard
      setTimeout(() => {
        const el = document.getElementById('leaderboard-anchor');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 150);
    } catch (err) {
      setError(err.message || 'Batch screening encountered an error.');
    } finally {
      setLoading(false);
      setLoadingStage('');
    }
  };

  return (
    <div className="app-layout">
      {/* Top Navigation */}
      <Navbar
        mode={mode}
        setMode={setMode}
        blindMode={blindMode}
        setBlindMode={setBlindMode}
        backendStatus={backendStatus}
      />

      {/* Hero Banner */}
      <section className="hero-banner">
        <div className="hero-inner">
          <div className="hero-pill-tag">
            <Sparkles size={14} className="text-violet" />
            <span>Next-Gen Talent Intelligence Engine</span>
          </div>
          <h1 className="hero-title">
            Intelligent Resume Screening, <br />
            <span className="text-gradient">Explainable AI Talent Fit</span>
          </h1>
          <p className="hero-description">
            Evaluate candidate suitability with dual-stage neural embeddings, categorized competency
            matrices, bias-free blind screening, and tailored interview probes.
          </p>
        </div>
      </section>

      {/* Main Workspace Container */}
      <main className="main-content-container">
        {/* Error Notification Callout */}
        {error && (
          <div className="alert-banner alert-banner-danger animate-fade-in">
            <AlertTriangle size={18} />
            <div className="alert-text-block">
              <span className="alert-title">Evaluation Error</span>
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

        {/* Primary CTA Trigger Section */}
        <div className="cta-action-bar">
          <div className="cta-hints">
            {blindMode && (
              <span className="pill pill-success">
                <Shield size={13} /> Bias-Free Blind Screening Active
              </span>
            )}
            <span className="cta-engine-info">
              Hybrid Transformer Embeddings + Random Forest Classifier + SHAP Explainability
            </span>
          </div>

          <button
            type="button"
            className="btn-primary btn-cta"
            disabled={loading}
            onClick={mode === 'single' ? handleScreenSingle : handleScreenBatch}
            id="btn-run-screening"
          >
            {loading ? (
              <>
                <Loader2 size={18} className="spinner-icon" />
                <span>{loadingStage || 'Processing AI Models...'}</span>
              </>
            ) : mode === 'single' ? (
              <>
                <Sparkles size={18} />
                <span>Screen Candidate Deep-Dive</span>
                <ArrowRight size={18} />
              </>
            ) : (
              <>
                <BarChart2 size={18} />
                <span>Rank & Benchmark Resumes</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </div>

        {/* RESULTS SECTION: SINGLE CANDIDATE DEEP-DIVE */}
        {mode === 'single' && evalResult && (
          <div id="evaluation-results-anchor" className="results-container animate-fade-in">
            <div className="results-header-bar">
              <div className="results-title-group">
                <h2 className="results-heading">Candidate Evaluation Report</h2>
                <p className="results-subheading">
                  Comprehensive audit for <strong>{evalResult.candidate}</strong> against target job description
                </p>
              </div>

              <button
                type="button"
                className="btn-secondary"
                onClick={() => setRawResumeCandidate(evalResult)}
              >
                Inspect Extracted Text
              </button>
            </div>

            {/* Score & Subscore Gauges */}
            <ScoreGauge
              fitScore={evalResult.fit_score}
              predictedCategory={evalResult.predicted_category}
              semanticSimilarity={evalResult.semantic_similarity}
              lexicalRelevance={evalResult.lexical_relevance || evalResult.jd_relevance}
              categoryAlignment={evalResult.category_alignment}
              confidence={evalResult.confidence}
              blindMode={evalResult.blind_mode}
              redactionCounts={evalResult.redaction_counts}
            />

            {/* Executive Recruiter Assessment Synthesis */}
            <NarrativeCard narrative={evalResult.narrative} />

            {/* Categorized Competencies Taxonomy Matrix */}
            <SkillsMatrix
              categorizedSkills={evalResult.categorized_skills}
              matchedKeywords={evalResult.matched_keywords}
              missingKeywords={evalResult.missing_keywords}
            />

            {/* Targeted Interview Probes Card */}
            {evalResult.narrative && evalResult.narrative.interview_questions && (
              <InterviewQuestionsCard
                questions={evalResult.narrative.interview_questions}
              />
            )}

            {/* SHAP Feature Importance Attribution */}
            {evalResult.shap_features && Object.keys(evalResult.shap_features).length > 0 && (
              <ShapVisualizer shapFeatures={evalResult.shap_features} />
            )}
          </div>
        )}

        {/* RESULTS SECTION: BATCH CANDIDATE LEADERBOARD */}
        {mode === 'batch' && batchResults && (
          <div id="leaderboard-anchor" className="results-container animate-fade-in">
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

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <span className="brand-title">HireLens<span className="brand-dot">.AI</span></span>
            <p className="footer-copyright">
              Enterprise-Grade Explainable Talent Intelligence Platform • Production Ready
            </p>
          </div>
          <div className="footer-tech-stack">
            <span className="tech-badge">FastAPI</span>
            <span className="tech-badge">PyTorch</span>
            <span className="tech-badge">Sentence-Transformers</span>
            <span className="tech-badge">SHAP XAI</span>
            <span className="tech-badge">React</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
