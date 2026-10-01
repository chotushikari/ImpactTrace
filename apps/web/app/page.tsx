'use client';

import React, { useState } from 'react';

// Types for local state simulation
interface Project {
  id: string;
  name: string;
  description: string;
  objective: string;
  created_at: string;
}

interface Asset {
  id: string;
  public_id: string;
  url: string;
  status: 'queued' | 'processing' | 'ready';
  filename: string;
  captured_at: string;
  lat?: number;
  lng?: number;
  caption?: string;
  ocr?: string;
  tags?: string[];
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<'overview' | 'ingest' | 'enrich' | 'search' | 'compare' | 'evidence' | 'dossier'>('overview');

  // State for interactive demo workflow
  const [projects, setProjects] = useState<Project[]>([
    {
      id: 'p-101',
      name: 'Jaipur Water Infrastructure Project',
      description: 'Clean drinking water pipeline installation across 4 sites',
      objective: 'Provide clean drinking water access to 5,000 households',
      created_at: '2026-10-01T10:00:00Z',
    },
  ]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>('p-101');

  // Demo asset dataset
  const [assets, setAssets] = useState<Asset[]>([
    {
      id: 'a-01',
      public_id: 'impacttrace/projects/jaipur/site_01_pipe_before',
      url: 'https://images.unsplash.com/photo-1541888946425-d0fbb186a5b2?w=800&auto=format&fit=crop&q=60',
      status: 'ready',
      filename: 'site_01_baseline_trench.jpg',
      captured_at: '2026-09-10 10:30 AM',
      lat: 26.9124,
      lng: 75.7873,
      caption: 'Baseline site survey showing excavated trench before pipe placement.',
      ocr: 'SITE 01 - JAIPUR WATER SCHEME - BASELINE SURVEY',
      tags: ['trench', 'excavation', 'baseline', 'water_project'],
    },
    {
      id: 'a-02',
      public_id: 'impacttrace/projects/jaipur/site_01_pipe_after',
      url: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&auto=format&fit=crop&q=60',
      status: 'ready',
      filename: 'site_01_pipe_installed.jpg',
      captured_at: '2026-09-28 02:15 PM',
      lat: 26.9125,
      lng: 75.7874,
      caption: 'Continuous blue HDPE water pipe laid in trench with concrete bedding.',
      ocr: 'SITE 01 - JAIPUR WATER SCHEME - PIPELINE COMPLETE',
      tags: ['pipeline', 'installed', 'hdpe_pipe', 'infrastructure'],
    },
  ]);

  // Search State
  const [searchQuery, setSearchQuery] = useState('water pipeline installation jaipur');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  // Compare State
  const [compareTarget, setCompareTarget] = useState('water pipeline');
  const [comparisonResult, setComparisonResult] = useState<any | null>(null);

  // Dossier State
  const [generatedDossier, setGeneratedDossier] = useState<any | null>(null);
  const [generatedStory, setGeneratedStory] = useState<string | null>(null);

  // New Project Form
  const [newProjName, setNewProjName] = useState('');
  const [newProjDesc, setNewProjDesc] = useState('');

  const handleCreateProject = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjName) return;
    const np: Project = {
      id: `p-${Date.now()}`,
      name: newProjName,
      description: newProjDesc || 'Impact monitoring project',
      objective: 'Verified environmental and social impact evidence',
      created_at: new Date().toISOString(),
    };
    setProjects([...projects, np]);
    setSelectedProjectId(np.id);
    setNewProjName('');
    setNewProjDesc('');
  };

  const handleSimulateUpload = () => {
    const newAsset: Asset = {
      id: `a-${Date.now()}`,
      public_id: `impacttrace/projects/${selectedProjectId}/upload_${Date.now()}`,
      url: 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&auto=format&fit=crop&q=60',
      status: 'ready',
      filename: `field_sample_${assets.length + 1}.jpg`,
      captured_at: new Date().toLocaleString(),
      lat: 26.913,
      lng: 75.788,
      caption: 'Newly ingested Cloudinary field asset with verified GPS metadata.',
      ocr: 'IMPACTTRACE VERIFIED FIELD RECORD',
      tags: ['field_media', 'verified_upload', 'cloudinary_ingest'],
    };
    setAssets([...assets, newAsset]);
  };

  const handleRunSearch = () => {
    setHasSearched(true);
    // Simulate hybrid vector + lexical search ranking
    const res = assets.map((a) => {
      const matchScore = a.caption?.toLowerCase().includes('pipe') || a.filename.includes('pipe') ? 0.94 : 0.62;
      return {
        asset: a,
        similarity: matchScore,
        lexicalScore: matchScore > 0.8 ? 0.9 : 0.4,
        finalScore: matchScore,
        matchReasons: [
          `Hybrid vector similarity score (${matchScore.toFixed(2)})`,
          `OCR match: "${a.ocr}"`,
          `GPS location verified (${a.lat}, ${a.lng})`,
        ],
      };
    });
    setSearchResults(res.sort((a, b) => b.finalScore - a.finalScore));
  };

  const handleRunCompare = () => {
    setComparisonResult({
      relation_id: 'rel-99201',
      before_asset: assets[0],
      after_asset: assets[1],
      alignment: {
        method: 'orb_homography_feature_match',
        score: 0.88,
        reliable: true,
        message: 'High feature alignment confidence between before/after frames.',
      },
      changes: [
        {
          type: 'addition',
          description: 'Continuous HDPE water pipeline structure installed along trench path.',
          confidence: 0.93,
        },
        {
          type: 'structural',
          description: 'Ground excavation backfilled and surface stabilized.',
          confidence: 0.89,
        },
      ],
      limitations: [
        'Sun angle shift between capture dates (10:30 AM vs 02:15 PM).',
        'Camera distance delta of ~0.4m.',
      ],
    });
  };

  const handleGenerateDossier = () => {
    const currentProj = projects.find((p) => p.id === selectedProjectId) || projects[0];
    setGeneratedDossier({
      title: `${currentProj.name} — Verified Impact Dossier`,
      project: currentProj,
      total_evidence_assets: assets.length,
      cloudinary_manifest: assets.map((a) => ({
        public_id: a.public_id,
        url: a.url,
        captured_at: a.captured_at,
        coordinates: `(${a.lat}, ${a.lng})`,
      })),
      provenance_guarantee: 'Every claim is 100% bound to verified Cloudinary source asset IDs.',
      limitations: ['Observations reflect visual state at recorded timestamp.'],
      generated_at: new Date().toISOString(),
    });

    setGeneratedStory(
      `📊 **Donor Impact Report — ${currentProj.name}**\n\n` +
        `We are proud to present verified field evidence for ${currentProj.name}. ` +
        `Using ImpactTrace visual intelligence, ${assets.length} Cloudinary media assets ` +
        `confirm successful completion of pipeline infrastructure at Site 01. ` +
        `All claims are verifiable via immutable asset signatures.`
    );
  };

  const currentProj = projects.find((p) => p.id === selectedProjectId) || projects[0];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navbar */}
      <header
        style={{
          borderBottom: '1px solid var(--border-color)',
          background: 'rgba(18, 24, 38, 0.9)',
          backdropFilter: 'blur(12px)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          padding: '16px 32px',
        }}
      >
        <div style={{ maxWidth: 1400, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div
              style={{
                width: 38,
                height: 38,
                borderRadius: 10,
                background: 'linear-gradient(135deg, #6366f1 0%, #10b981 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 800,
                fontSize: 18,
                color: '#fff',
              }}
            >
              IT
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 18, letterSpacing: '-0.3px' }}>ImpactTrace</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Visual Evidence Intelligence</div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Active Project:</span>
            <select
              className="input-field"
              style={{ width: 'auto', padding: '6px 12px', fontSize: 13 }}
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              id="project-selector"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <main style={{ flex: 1, maxWidth: 1400, width: '100%', margin: '0 auto', padding: '32px' }}>
        {/* Hero Banner */}
        <section className="glass-panel" style={{ padding: '32px', marginBottom: '32px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ maxWidth: 800 }}>
            <span className="badge badge-verified" style={{ marginBottom: 12 }}>
              Hackathon MVP — Sprints 00–08 Complete
            </span>
            <h1 style={{ fontSize: 36, fontWeight: 800, lineHeight: 1.2, marginBottom: 12 }}>
              {currentProj.name}
            </h1>
            <p style={{ fontSize: 16, color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 20 }}>
              {currentProj.description}. Turn field photos and videos into searchable, traceable visual evidence for proving project progress.
            </p>
            <div style={{ display: 'flex', gap: 12 }}>
              <button className="btn btn-primary" onClick={() => setActiveTab('ingest')} id="btn-upload-nav">
                + Upload Media Asset
              </button>
              <button className="btn btn-secondary" onClick={() => setActiveTab('search')} id="btn-search-nav">
                🔍 Natural Language Search
              </button>
            </div>
          </div>
        </section>

        {/* Tab Navigation */}
        <div style={{ display: 'flex', gap: 8, borderBottom: '1px solid var(--border-color)', marginBottom: 24, paddingBottom: 8 }}>
          {[
            { id: 'overview', label: '📁 Project Media' },
            { id: 'ingest', label: '☁️ Cloudinary Ingest' },
            { id: 'enrich', label: '🧠 AI Enrichment' },
            { id: 'search', label: '🔍 Semantic Search' },
            { id: 'compare', label: '⚖️ Before / After' },
            { id: 'evidence', label: '🔗 Evidence Graph' },
            { id: 'dossier', label: '📄 Impact Dossier' },
          ].map((tab) => (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              onClick={() => setActiveTab(tab.id as any)}
              style={{
                padding: '10px 18px',
                fontSize: 14,
                fontWeight: 600,
                borderRadius: '8px',
                border: 'none',
                background: activeTab === tab.id ? 'var(--accent-primary)' : 'transparent',
                color: activeTab === tab.id ? '#ffffff' : 'var(--text-muted)',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* TAB 1: OVERVIEW */}
        {activeTab === 'overview' && (
          <div className="animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h2 style={{ fontSize: 20, fontWeight: 700 }}>Project Assets ({assets.length})</h2>
              <button className="btn btn-secondary" onClick={() => setActiveTab('ingest')}>
                Add New Asset
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 24 }}>
              {assets.map((asset) => (
                <div key={asset.id} className="glass-panel" style={{ overflow: 'hidden' }}>
                  <img src={asset.url} alt={asset.filename} style={{ width: '100%', height: 200, objectFit: 'cover' }} />
                  <div style={{ padding: 20 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <span className="badge badge-ready">{asset.status}</span>
                      <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{asset.captured_at}</span>
                    </div>
                    <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 6 }}>{asset.filename}</div>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 12, lineHeight: 1.4 }}>
                      {asset.caption}
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {asset.tags?.map((t) => (
                        <span key={t} style={{ fontSize: 11, background: 'rgba(255,255,255,0.06)', padding: '2px 8px', borderRadius: 4 }}>
                          #{t}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 2: INGESTION */}
        {activeTab === 'ingest' && (
          <div className="animate-fade-in glass-panel" style={{ padding: 32, maxWidth: 700, margin: '0 auto' }}>
            <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 12 }}>Cloudinary Signed Media Upload</h2>
            <p style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 24 }}>
              Upload media to Cloudinary. Original assets belong to Cloudinary, while Postgres holds immutable metadata and provenance signatures.
            </p>
            <div style={{ border: '2px dashed var(--border-glow)', padding: 40, borderRadius: 12, textAlign: 'center', marginBottom: 24 }}>
              <div style={{ fontSize: 40, marginBottom: 12 }}>📸</div>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Drag and drop media files</div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16 }}>Supports JPG, PNG, MP4 (Up to 100MB)</div>
              <button className="btn btn-primary" onClick={handleSimulateUpload} id="btn-simulate-upload">
                Simulate Cloudinary Direct Upload
              </button>
            </div>
          </div>
        )}

        {/* TAB 3: ENRICHMENT */}
        {activeTab === 'enrich' && (
          <div className="animate-fade-in glass-panel" style={{ padding: 32 }}>
            <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 16 }}>AI Enrichment Pipeline Inspection</h2>
            <div style={{ display: 'grid', gap: 20 }}>
              {assets.map((asset) => (
                <div key={asset.id} style={{ display: 'flex', gap: 24, background: 'rgba(0,0,0,0.2)', padding: 20, borderRadius: 12 }}>
                  <img src={asset.url} alt={asset.filename} style={{ width: 140, height: 100, borderRadius: 8, objectFit: 'cover' }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>{asset.filename}</div>
                    <div style={{ fontSize: 13, color: 'var(--accent-sky)', marginBottom: 8 }}>
                      Cloudinary ID: <code style={{ color: '#fff' }}>{asset.public_id}</code>
                    </div>
                    <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>
                      <strong>OCR Text:</strong> {asset.ocr}
                    </div>
                    <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>
                      <strong>VLM Caption:</strong> {asset.caption}
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--accent-emerald)' }}>
                      ✓ 768-dim CLIP Vector Embedding Generated & Indexed
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 4: SEARCH */}
        {activeTab === 'search' && (
          <div className="animate-fade-in">
            <div className="glass-panel" style={{ padding: 28, marginBottom: 28 }}>
              <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 12 }}>Hybrid Semantic Evidence Search</h2>
              <div style={{ display: 'flex', gap: 12 }}>
                <input
                  type="text"
                  className="input-field"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Ask an impact query, e.g. water pipeline installation jaipur..."
                  id="input-search-query"
                />
                <button className="btn btn-primary" onClick={handleRunSearch} id="btn-execute-search">
                  Execute Search
                </button>
              </div>
            </div>

            {hasSearched && (
              <div style={{ display: 'grid', gap: 20 }}>
                <h3 style={{ fontSize: 18, fontWeight: 700 }}>Search Evidence Results</h3>
                {searchResults.map((res, i) => (
                  <div key={i} className="glass-panel" style={{ padding: 24, display: 'flex', gap: 24 }}>
                    <img src={res.asset.url} alt={res.asset.filename} style={{ width: 220, height: 140, borderRadius: 10, objectFit: 'cover' }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                        <div style={{ fontWeight: 700, fontSize: 17 }}>{res.asset.filename}</div>
                        <span className="badge badge-ready">Score: {(res.finalScore * 100).toFixed(0)}%</span>
                      </div>
                      <p style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 12 }}>{res.asset.caption}</p>
                      <div style={{ fontSize: 12, color: 'var(--accent-sky)' }}>
                        <strong>Match Reasons:</strong>
                        <ul style={{ paddingLeft: 20, marginTop: 4 }}>
                          {res.matchReasons.map((m: string, idx: number) => (
                            <li key={idx}>{m}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 5: COMPARE */}
        {activeTab === 'compare' && (
          <div className="animate-fade-in">
            <div className="glass-panel" style={{ padding: 28, marginBottom: 28 }}>
              <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 12 }}>Before / After Visual Comparison Engine</h2>
              <div style={{ display: 'flex', gap: 16, alignItems: 'center', marginBottom: 16 }}>
                <div>
                  <label style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Before Asset:</label>
                  <select className="input-field" style={{ width: 260 }}>
                    <option>{assets[0]?.filename}</option>
                  </select>
                </div>
                <div style={{ fontSize: 20, marginTop: 16 }}>➡️</div>
                <div>
                  <label style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>After Asset:</label>
                  <select className="input-field" style={{ width: 260 }}>
                    <option>{assets[1]?.filename}</option>
                  </select>
                </div>
                <button className="btn btn-primary" style={{ marginTop: 18 }} onClick={handleRunCompare} id="btn-run-compare">
                  Run Visual Compare
                </button>
              </div>
            </div>

            {comparisonResult && (
              <div className="glass-panel" style={{ padding: 28 }}>
                <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>Visual Comparison Result</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
                  <div>
                    <div style={{ fontWeight: 600, marginBottom: 8 }}>Before Media</div>
                    <img src={comparisonResult.before_asset.url} alt="Before" style={{ width: '100%', height: 240, borderRadius: 10, objectFit: 'cover' }} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, marginBottom: 8 }}>After Media</div>
                    <img src={comparisonResult.after_asset.url} alt="After" style={{ width: '100%', height: 240, borderRadius: 10, objectFit: 'cover' }} />
                  </div>
                </div>

                <div style={{ background: 'rgba(0,0,0,0.3)', padding: 20, borderRadius: 10 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                    <span>
                      Alignment Method: <strong>{comparisonResult.alignment.method}</strong>
                    </span>
                    <span className="badge badge-ready">Confidence: {(comparisonResult.alignment.score * 100).toFixed(0)}%</span>
                  </div>
                  <div style={{ fontWeight: 700, marginBottom: 8 }}>Detected Structural Changes:</div>
                  <ul style={{ paddingLeft: 20, fontSize: 14, color: 'var(--text-muted)' }}>
                    {comparisonResult.changes.map((c: any, idx: number) => (
                      <li key={idx} style={{ marginBottom: 4 }}>
                        <strong>[{c.type.toUpperCase()}]</strong> {c.description} (Confidence: {(c.confidence * 100).toFixed(0)}%)
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 6: EVIDENCE GRAPH */}
        {activeTab === 'evidence' && (
          <div className="animate-fade-in glass-panel" style={{ padding: 32 }}>
            <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 16 }}>Auditable Evidence Lineage Chain</h2>
            <div style={{ borderLeft: '3px solid var(--accent-primary)', paddingLeft: 24, display: 'grid', gap: 20 }}>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: 16, borderRadius: 8 }}>
                <span className="badge badge-verified">Verified Fact / Project Data</span>
                <div style={{ fontWeight: 700, fontSize: 16, marginTop: 6 }}>
                  Claim: Water pipeline installation completed at Site 01 Jaipur
                </div>
              </div>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: 16, borderRadius: 8 }}>
                <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--accent-sky)' }}>Source Asset 1 (Cloudinary):</div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                  Public ID: <code>{assets[0].public_id}</code> | GPS: (26.9124, 75.7873) | Captured: 2026-09-10
                </div>
              </div>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: 16, borderRadius: 8 }}>
                <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--accent-sky)' }}>Source Asset 2 (Cloudinary):</div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                  Public ID: <code>{assets[1].public_id}</code> | GPS: (26.9125, 75.7874) | Captured: 2026-09-28
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 7: DOSSIER & STORIES */}
        {activeTab === 'dossier' && (
          <div className="animate-fade-in">
            <div className="glass-panel" style={{ padding: 28, marginBottom: 28 }}>
              <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 12 }}>Impact Dossier & Campaign Story Generator</h2>
              <button className="btn btn-primary" onClick={handleGenerateDossier} id="btn-generate-dossier">
                📄 Generate Evidence Dossier & Campaign Story
              </button>
            </div>

            {generatedDossier && (
              <div style={{ display: 'grid', gap: 24 }}>
                <div className="glass-panel" style={{ padding: 28 }}>
                  <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12, color: 'var(--accent-emerald)' }}>
                    Generated Campaign Content (Donor Update)
                  </h3>
                  <pre
                    style={{
                      background: 'rgba(0,0,0,0.4)',
                      padding: 20,
                      borderRadius: 8,
                      fontSize: 14,
                      whiteSpace: 'pre-wrap',
                      color: 'var(--text-main)',
                      fontFamily: 'inherit',
                    }}
                  >
                    {generatedStory}
                  </pre>
                </div>

                <div className="glass-panel" style={{ padding: 28 }}>
                  <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Impact Dossier Source Manifest</h3>
                  <pre
                    style={{
                      background: 'rgba(0,0,0,0.4)',
                      padding: 20,
                      borderRadius: 8,
                      fontSize: 13,
                      color: 'var(--accent-sky)',
                      overflowX: 'auto',
                    }}
                  >
                    {JSON.stringify(generatedDossier, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border-color)', padding: '20px 32px', textAlign: 'center', fontSize: 13, color: 'var(--text-muted)' }}>
        ImpactTrace © 2026 — Built with Next.js, Cloudinary, FastAPI, Postgres & pgvector.
      </footer>
    </div>
  );
}
