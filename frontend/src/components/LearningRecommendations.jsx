import React, { useState } from 'react';
import { PlayCircle, ExternalLink, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';

function formatViewCount(n) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M views`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K views`;
  return `${n} views`;
}

export default function LearningRecommendations({ skillGaps = {}, jobRole = '' }) {
  const missingSkills = skillGaps.missing_skills || [];
  const presentSkills = skillGaps.present_skills || [];

  const [selectedSkill, setSelectedSkill] = useState(null);
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSelectSkill = async (skill) => {
    if (selectedSkill === skill) {
      // Toggle off if clicking the same skill again
      setSelectedSkill(null);
      setVideos([]);
      return;
    }
    setSelectedSkill(skill);
    setVideos([]);
    setError(null);
    setLoading(true);
    try {
      const response = await fetch(`/api/youtube-tutorials?skill=${encodeURIComponent(skill)}&job_role=${encodeURIComponent(jobRole)}`);
      const data = await response.json();
      if (data.videos && data.videos.length > 0) {
        setVideos(data.videos);
      } else {
        setError('No tutorials found for this skill right now.');
      }
    } catch {
      setError('Could not load tutorials -- check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  if (missingSkills.length === 0 && presentSkills.length === 0) {
    return null;
  }

  return (
    <div className="glass-panel narrative-card">
      <div className="section-header">
        <div className="section-title-group">
          <div>
            <h2 className="section-title">Skills to build</h2>
            <p className="section-subtitle">
              Curated, vocabulary-independent skill matching -- click a skill to see top tutorials
            </p>
          </div>
        </div>
      </div>

      {missingSkills.length > 0 && (
        <div style={{ marginBottom: presentSkills.length > 0 ? '18px' : '0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }} className="text-warning">
            <AlertCircle size={15} />
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Not yet on the resume ({missingSkills.length})</span>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {missingSkills.map((skill) => (
              <button
                key={skill}
                type="button"
                onClick={() => handleSelectSkill(skill)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  background: selectedSkill === skill ? 'var(--color-warning-border)' : 'var(--color-warning-bg)',
                  border: '1px solid var(--color-warning-border)',
                  color: 'var(--color-warning)', borderRadius: '7px', padding: '6px 14px',
                  fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer',
                }}
              >
                <PlayCircle size={14} />
                {skill}
              </button>
            ))}
          </div>
        </div>
      )}

      {presentSkills.length > 0 && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }} className="text-emerald">
            <CheckCircle2 size={15} />
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Already covered ({presentSkills.length})</span>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {presentSkills.map((skill) => (
              <span
                key={skill}
                style={{
                  background: 'var(--color-success-bg)', border: '1px solid var(--color-success-border)',
                  color: 'var(--color-success)', borderRadius: '7px', padding: '5px 14px',
                  fontSize: '0.85rem', fontWeight: 500,
                }}
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {selectedSkill && (
        <div style={{ marginTop: '20px', borderTop: '1px solid var(--border-subtle)', paddingTop: '16px' }}>
          <p style={{ fontSize: '0.85rem', marginBottom: '12px', color: 'var(--text-secondary)' }}>
            Top tutorials for <strong>{selectedSkill}</strong>:
          </p>

          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
              <Loader2 size={16} className="spinner-icon" /> Loading tutorials...
            </div>
          )}

          {error && !loading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }} className="text-warning">
              <AlertCircle size={15} /> {error}
            </div>
          )}

          {!loading && !error && videos.length > 0 && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '14px' }}>
              {videos.map((video) => (
                <a
                  key={video.video_id}
                  href={video.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display: 'block', textDecoration: 'none', color: 'inherit',
                    background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)',
                    borderRadius: '10px', overflow: 'hidden',
                  }}
                >
                  <img
                    src={video.thumbnail}
                    alt={video.title}
                    style={{ width: '100%', display: 'block', aspectRatio: '16/9', objectFit: 'cover' }}
                  />
                  <div style={{ padding: '10px 12px' }}>
                    <div style={{
                      fontSize: '0.85rem', fontWeight: 600, lineHeight: 1.35, marginBottom: '6px',
                      display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden',
                    }}>
                      {video.title}
                    </div>
                    <div style={{ fontSize: '0.75rem', opacity: 0.6, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>{video.channel}</span>
                      <ExternalLink size={12} />
                    </div>
                    <div style={{ fontSize: '0.75rem', opacity: 0.5, marginTop: '3px' }}>
                      {formatViewCount(video.view_count)}
                    </div>
                  </div>
                </a>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
