import React, { useState, useEffect } from 'react';
import { X, Copy, Check, Search } from 'lucide-react';

export default function ResumeInspectorModal({
  candidate,
  onClose,
}) {
  const [copied, setCopied] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!candidate) return null;

  const rawText = candidate.raw_text || '';

  const handleCopy = () => {
    navigator.clipboard.writeText(rawText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-container resume-inspector-modal"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-group">
            <div>
              <h3 className="modal-title">Extracted Resume Content</h3>
              <p className="modal-subtitle">
                {candidate.candidate} • {candidate.filename}
              </p>
            </div>
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={handleCopy}
            >
              {copied ? <Check size={14} className="text-emerald" /> : <Copy size={14} />}
              <span>{copied ? 'Copied' : 'Copy Text'}</span>
            </button>
            <button
              type="button"
              className="btn-icon-ghost"
              onClick={onClose}
              title="Close modal"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Search inside resume */}
        <div className="modal-search-bar">
          <Search size={15} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search keywords inside resume text..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          <pre className="resume-raw-pre">
            {rawText || 'No text extracted for this resume.'}
          </pre>
        </div>
      </div>
    </div>
  );
}
