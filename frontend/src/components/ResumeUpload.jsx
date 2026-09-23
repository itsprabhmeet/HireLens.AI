import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  X,
  FileText,
  Clipboard,
  Layers,
  CheckCircle2,
} from 'lucide-react';

export default function ResumeUpload({
  mode,
  resumeFile,
  setResumeFile,
  resumeText,
  setResumeText,
  batchFiles,
  setBatchFiles,
}) {
  const [inputTab, setInputTab] = useState('upload'); // 'upload' | 'paste'
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const batchInputRef = useRef(null);

  // Drag & drop handlers for single file
  const handleSingleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleSingleDragLeave = () => {
    setIsDragging(false);
  };

  const handleSingleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      setResumeFile(file);
      setResumeText('');
    }
  };

  const handleSingleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setResumeFile(e.target.files[0]);
      setResumeText('');
    }
  };

  // Drag & drop handlers for batch files
  const handleBatchDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const newFiles = Array.from(e.dataTransfer.files);
      setBatchFiles((prev) => [...prev, ...newFiles]);
    }
  };

  const handleBatchFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      setBatchFiles((prev) => [...prev, ...newFiles]);
    }
  };

  const removeBatchFile = (indexToRemove) => {
    setBatchFiles((prev) => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div className="glass-panel resume-upload-card">
      <div className="section-header">
        <div className="section-title-group">
          <div>
            <h2 className="section-title">
              {mode === 'single' ? 'Resume' : 'Resumes'}
            </h2>
            <p className="section-subtitle">
              {mode === 'single'
                ? 'Upload a PDF, DOCX, or TXT file, or paste the text directly'
                : 'Upload multiple resumes to rank against the same job description'}
            </p>
          </div>
        </div>

        {/* Mode-specific actions */}
        {mode === 'single' ? (
          <div className="input-tab-pills">
            <button
              type="button"
              className={`input-tab-btn ${inputTab === 'upload' ? 'input-tab-btn-active' : ''}`}
              onClick={() => setInputTab('upload')}
            >
              <UploadCloud size={14} /> File Upload
            </button>
            <button
              type="button"
              className={`input-tab-btn ${inputTab === 'paste' ? 'input-tab-btn-active' : ''}`}
              onClick={() => setInputTab('paste')}
            >
              <Clipboard size={14} /> Paste Text
            </button>
          </div>
        ) : (
          batchFiles.length > 0 && (
            <button
              type="button"
              className="btn-ghost text-danger"
              onClick={() => setBatchFiles([])}
            >
              Clear All ({batchFiles.length})
            </button>
          )
        )}
      </div>


      {/* SINGLE MODE CONTENT */}
      {mode === 'single' && (
        <>
          {inputTab === 'upload' ? (
            <div className="upload-container">
              {resumeFile ? (
                <div className="selected-file-card">
                  <div className="file-info-group">
                    <div className="file-icon-wrapper">
                      <FileText size={28} className="text-indigo" />
                    </div>
                    <div className="file-meta">
                      <span className="file-name">{resumeFile.name}</span>
                      <span className="file-size">
                        {formatFileSize(resumeFile.size)}
                      </span>
                    </div>
                  </div>
                  <button
                    type="button"
                    className="btn-icon-danger"
                    onClick={() => setResumeFile(null)}
                    title="Remove file"
                  >
                    <X size={16} />
                  </button>
                </div>
              ) : (
                <div
                  className={`dropzone ${isDragging ? 'dropzone-active' : ''}`}
                  onDragOver={handleSingleDragOver}
                  onDragLeave={handleSingleDragLeave}
                  onDrop={handleSingleDrop}
                  onClick={() => fileInputRef.current && fileInputRef.current.click()}
                  role="button"
                  tabIndex={0}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx,.txt"
                    onChange={handleSingleFileChange}
                    style={{ display: 'none' }}
                  />
                  <div className="dropzone-icon-circle">
                    <UploadCloud size={26} className="text-muted" />
                  </div>
                  <p className="dropzone-main-text">
                    Drag and drop resume here, or <span className="text-indigo-bold">browse file</span>
                  </p>
                  <p className="dropzone-sub-text">
                    PDF, DOCX, or TXT — up to 15MB
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="paste-container">
              <textarea
                className="resume-textarea"
                rows={7}
                value={resumeText}
                onChange={(e) => {
                  setResumeText(e.target.value);
                  setResumeFile(null);
                }}
                placeholder="Paste candidate resume content here..."
                id="input-resume-text"
              />
              <div className="jd-stats-bar">
                <span className="jd-stat-item">
                  <FileText size={13} /> {resumeText.trim() ? resumeText.trim().split(/\s+/).length : 0} words
                </span>
                <span className="jd-stat-divider">•</span>
                <span className="jd-stat-item">{resumeText.length} characters</span>
              </div>
            </div>
          )}
        </>
      )}

      {/* BATCH MODE CONTENT */}
      {mode === 'batch' && (
        <div className="batch-upload-container">
          <div
            className={`dropzone ${isDragging ? 'dropzone-active' : ''}`}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleBatchDrop}
            onClick={() => batchInputRef.current && batchInputRef.current.click()}
            role="button"
            tabIndex={0}
          >
            <input
              ref={batchInputRef}
              type="file"
              multiple
              accept=".pdf,.docx,.txt"
              onChange={handleBatchFileChange}
              style={{ display: 'none' }}
            />
            <div className="dropzone-icon-circle">
              <Layers size={26} className="text-muted" />
            </div>
            <p className="dropzone-main-text">
              Drop multiple resumes here, or <span className="text-cyan-bold">browse folder</span>
            </p>
            <p className="dropzone-sub-text">
              Up to 50 resumes — you can filter and export the ranking afterward
            </p>
          </div>

          {/* Batch Files List */}
          {batchFiles.length > 0 && (
            <div className="batch-files-list">
              <div className="batch-list-header">
                <span className="batch-count-badge">
                  <CheckCircle2 size={14} className="text-emerald" /> {batchFiles.length} resume{batchFiles.length === 1 ? '' : 's'} staged
                </span>
              </div>
              <div className="batch-items-grid">
                {batchFiles.map((file, idx) => (
                  <div key={`${file.name}-${idx}`} className="batch-item-card">
                    <FileText size={16} className="text-secondary" />
                    <span className="batch-file-title" title={file.name}>{file.name}</span>
                    <span className="batch-file-size">{formatFileSize(file.size)}</span>
                    <button
                      type="button"
                      className="batch-item-remove"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeBatchFile(idx);
                      }}
                      title="Remove file"
                    >
                      <X size={13} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
