import React, { useState, useMemo } from 'react';
import {
  Search,
  Download,
  Eye,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

export default function LeaderboardTable({
  candidates = [],
  blindMode = false,
  onSelectCandidate,
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [tierFilter, setTierFilter] = useState('all'); // 'all' | 'strong' | 'potential' | 'low'
  const [sortAsc, setSortAsc] = useState(false);

  // Filter & sort candidates
  const filteredCandidates = useMemo(() => {
    return candidates
      .filter((cand) => {
        // Tier filter
        if (tierFilter === 'strong' && cand.fit_score < 75) return false;
        if (tierFilter === 'potential' && (cand.fit_score < 50 || cand.fit_score >= 75)) return false;
        if (tierFilter === 'low' && cand.fit_score >= 50) return false;

        // Search query
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const matchName = (cand.candidate || '').toLowerCase().includes(q);
          const matchFile = (cand.filename || '').toLowerCase().includes(q);
          const matchCat = (cand.predicted_category || '').toLowerCase().includes(q);
          const matchSkills = (cand.matched_keywords || []).some((k) =>
            (Array.isArray(k) ? k[0] : k).toLowerCase().includes(q)
          );
          return matchName || matchFile || matchCat || matchSkills;
        }

        return true;
      })
      .sort((a, b) => {
        return sortAsc ? a.fit_score - b.fit_score : b.fit_score - a.fit_score;
      });
  }, [candidates, searchQuery, tierFilter, sortAsc]);

  // CSV Export functionality
  const handleExportCSV = () => {
    if (candidates.length === 0) return;

    const headers = [
      'Rank',
      'Candidate',
      'Filename',
      'Fit Score (%)',
      'Tier',
      'Predicted Role',
      'Semantic Match (%)',
      'Matched Skills Count',
      'Missing Skills Count',
    ];

    const rows = candidates.map((cand, idx) => {
      let tier = 'Low Match';
      if (cand.fit_score >= 75) tier = 'Strong Match';
      else if (cand.fit_score >= 50) tier = 'Potential Match';

      return [
        idx + 1,
        `"${cand.candidate || ''}"`,
        `"${cand.filename || ''}"`,
        cand.fit_score.toFixed(1),
        `"${tier}"`,
        `"${cand.predicted_category || ''}"`,
        cand.semantic_similarity > 1.0 ? Math.round(cand.semantic_similarity) : Math.round((cand.semantic_similarity || 0) * 100),
        cand.matched_count || (cand.matched_keywords ? cand.matched_keywords.length : 0),
        cand.missing_count || (cand.missing_keywords ? cand.missing_keywords.length : 0),
      ];
    });

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `HireLens_Leaderboard_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="glass-panel leaderboard-card">
      <div className="section-header leaderboard-header">
        <div className="section-title-group">
          <div>
            <h2 className="section-title">Ranking</h2>
            <p className="section-subtitle">
              Candidates ranked against the job description
            </p>
          </div>
        </div>

        {/* Export CSV action */}
        <button
          type="button"
          className="btn-secondary"
          onClick={handleExportCSV}
          disabled={candidates.length === 0}
        >
          <Download size={14} />
          <span>Export CSV</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="leaderboard-controls-bar">
        {/* Search Input */}
        <div className="search-input-wrapper">
          <Search size={15} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search by candidate name, file, role, or matched skill..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Tier filter tabs */}
        <div className="tier-filter-pills">
          <button
            type="button"
            className={`tier-pill-btn ${tierFilter === 'all' ? 'tier-pill-active' : ''}`}
            onClick={() => setTierFilter('all')}
          >
            All ({candidates.length})
          </button>
          <button
            type="button"
            className={`tier-pill-btn ${tierFilter === 'strong' ? 'tier-pill-active' : ''}`}
            onClick={() => setTierFilter('strong')}
          >
            Strong Match (75%+)
          </button>
          <button
            type="button"
            className={`tier-pill-btn ${tierFilter === 'potential' ? 'tier-pill-active' : ''}`}
            onClick={() => setTierFilter('potential')}
          >
            Potential (50-74%)
          </button>
          <button
            type="button"
            className={`tier-pill-btn ${tierFilter === 'low' ? 'tier-pill-active' : ''}`}
            onClick={() => setTierFilter('low')}
          >
            Low (&lt;50%)
          </button>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="table-responsive">
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th className="th-rank">Rank</th>
              <th className="th-candidate">Candidate Profile</th>
              <th
                className="th-score th-sortable"
                onClick={() => setSortAsc(!sortAsc)}
                title="Click to sort"
              >
                <span>Fit Score</span>
                {sortAsc ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </th>
              <th className="th-tier">Status Tier</th>
              <th className="th-domain">Predicted Role</th>
              <th className="th-skills">Skills Match</th>
              <th className="th-action">Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredCandidates.map((cand, idx) => {
              const rank = idx + 1;
              const score = Math.round(cand.fit_score * 10) / 10;

              // Tier styling
              let tierClass = 'pill-danger';
              let tierText = 'Low Match';
              if (score >= 75) {
                tierClass = 'pill-success';
                tierText = 'Strong Match';
              } else if (score >= 50) {
                tierClass = 'pill-warning';
                tierText = 'Potential Match';
              }

              // Top 3 Medal Badges
              let medalIcon = null;
              if (rank === 1) medalIcon = <span className="rank-medal gold">🥇</span>;
              else if (rank === 2) medalIcon = <span className="rank-medal silver">🥈</span>;
              else if (rank === 3) medalIcon = <span className="rank-medal bronze">🥉</span>;

              return (
                <tr
                  key={cand.id || idx}
                  className="leaderboard-row"
                  onClick={() => onSelectCandidate(cand)}
                >
                  <td className="td-rank">
                    <div className="rank-badge-wrapper">
                      {medalIcon || <span className="rank-number">#{rank}</span>}
                    </div>
                  </td>

                  <td className="td-candidate">
                    <div className="candidate-cell">
                      <span className="candidate-name">{cand.candidate}</span>
                      <span className="candidate-filename">{cand.filename}</span>
                    </div>
                  </td>

                  <td className="td-score">
                    <div className="score-cell">
                      <span className="score-number">{score}%</span>
                      <div className="score-mini-bar">
                        <div
                          className={`score-mini-fill ${
                            score >= 75 ? 'fill-emerald' : score >= 50 ? 'fill-amber' : 'fill-rose'
                          }`}
                          style={{ width: `${Math.min(100, score)}%` }}
                        />
                      </div>
                    </div>
                  </td>

                  <td className="td-tier">
                    <span className={`pill ${tierClass}`}>{tierText}</span>
                  </td>

                  <td className="td-domain">
                    <span className="pill pill-brand">
                      {cand.predicted_category || 'General'}
                    </span>
                  </td>

                  <td className="td-skills">
                    <div className="skills-summary-cell">
                      <span className="skill-count text-emerald">
                        <CheckCircle2 size={13} />{' '}
                        {cand.matched_count || (cand.matched_keywords ? cand.matched_keywords.length : 0)} Matched
                      </span>
                      <span className="skill-count text-warning">
                        <AlertCircle size={13} />{' '}
                        {cand.missing_count || (cand.missing_keywords ? cand.missing_keywords.length : 0)} Missing
                      </span>
                    </div>
                  </td>

                  <td className="td-action">
                    <button
                      type="button"
                      className="btn-inspect"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectCandidate(cand);
                      }}
                      title="Inspect in-depth analysis"
                    >
                      <Eye size={14} />
                      <span>Inspect</span>
                    </button>
                  </td>
                </tr>
              );
            })}

            {filteredCandidates.length === 0 && (
              <tr>
                <td colSpan={7} className="table-empty-cell">
                  <p>No candidates match your current search or tier filter.</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
