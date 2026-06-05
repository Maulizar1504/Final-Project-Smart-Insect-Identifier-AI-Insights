'use client';

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface Prediction {
  class: string;
  prob:  number;
}

interface ResultProps {
  result: {
    top_prediction: string;
    predictions:    Prediction[];
    ai_insight:     string;
  };
}

export default function ResultCard({ result }: ResultProps) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 80);
    return () => clearTimeout(t);
  }, []);

  const topProb = result.predictions?.[0]?.prob ?? 0;

  const confLevel = topProb >= 0.8 ? 'Tinggi' : topProb >= 0.5 ? 'Sedang' : 'Rendah';

  const confStyle = {
    Tinggi: { color: '#3a9b5c', bg: 'rgba(58,155,92,0.10)',  border: 'rgba(58,155,92,0.25)'  },
    Sedang: { color: '#d4921a', bg: 'rgba(212,146,26,0.10)', border: 'rgba(212,146,26,0.25)' },
    Rendah: { color: '#e05a4a', bg: 'rgba(224,90,74,0.10)',  border: 'rgba(224,90,74,0.25)'  },
  }[confLevel];

  return (
    <div
      className="rounded-2xl p-8 shadow-2xl"
      style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}
    >

      {/* ── Top prediction ──────────────────── */}
      <div
        className="flex items-start justify-between gap-4 pb-6 mb-6"
        style={{ borderBottom: '1px solid var(--border)' }}
      >
        <div>
          <p
            className="text-xs tracking-widest uppercase font-medium mb-2"
            style={{ color: 'var(--text-muted)' }}
          >
            Prediksi Teratas
          </p>
          <h2
            className="font-display text-3xl font-bold capitalize leading-tight"
            style={{ color: 'var(--text)' }}
          >
            {(result.top_prediction ?? '').replace(/_/g, ' ')}
          </h2>
        </div>

        <div className="shrink-0 text-right">
          <p
            className="text-xs tracking-widest uppercase font-medium mb-2"
            style={{ color: 'var(--text-muted)' }}
          >
            Kepercayaan
          </p>
          <span
            className="text-xs font-semibold px-3 py-1 rounded-full"
            style={{
              color:      confStyle.color,
              background: confStyle.bg,
              border:     `1px solid ${confStyle.border}`,
            }}
          >
            {confLevel}
          </span>
        </div>
      </div>

      {/* ── Probability bars ────────────────── */}
      <div
        className="pb-6 mb-6 space-y-4"
        style={{ borderBottom: '1px solid var(--border)' }}
      >
        <p
          className="text-xs tracking-widest uppercase font-medium"
          style={{ color: 'var(--text-muted)' }}
        >
          Distribusi Probabilitas
        </p>

        {(result.predictions ?? []).map((p, idx) => {
          const pct   = (p.prob ?? 0) * 100;
          const isTop = idx === 0;
          const label = (p.class ?? '').replace(/_/g, ' ') || `Kelas ${idx + 1}`;

          return (
            <div key={idx}>
              <div className="flex justify-between items-baseline mb-1.5">
                <span
                  className="text-sm capitalize"
                  style={{ color: isTop ? 'var(--text)' : 'var(--text-muted)' }}
                >
                  {label}
                </span>
                <span
                  className="text-xs font-mono tabular-nums"
                  style={{ color: isTop ? 'var(--amber-light)' : 'var(--text-muted)' }}
                >
                  {pct.toFixed(1)}%
                </span>
              </div>
              <div
                className="h-1.5 rounded-full overflow-hidden"
                style={{ background: 'var(--surface-2)' }}
              >
                <div
                  className="h-full rounded-full transition-all ease-out"
                  style={{
                    width:              animated ? `${pct.toFixed(1)}%` : '0%',
                    transitionDuration: `${700 + idx * 100}ms`,
                    transitionDelay:    `${idx * 80}ms`,
                    background:         isTop
                      ? 'linear-gradient(90deg, var(--amber), var(--amber-light))'
                      : 'rgba(212,146,26,0.30)',
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* ── AI Insight ──────────────────────── */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <div
            className="w-5 h-5 rounded flex items-center justify-center"
            style={{ background: 'var(--amber-dim)', border: '1px solid var(--border)' }}
          >
            <svg
              className="w-3 h-3"
              fill="none" viewBox="0 0 24 24" stroke="currentColor"
              style={{ color: 'var(--amber)' }}
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h3
            className="text-sm font-semibold tracking-wide"
            style={{ color: 'var(--text)' }}
          >
            AI Insights
          </h3>
        </div>

        <div
          className="prose prose-invert prose-sm max-w-none leading-relaxed"
          style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-dm-sans, system-ui)' }}
        >
          <ReactMarkdown>
            {result.ai_insight ?? ''}
          </ReactMarkdown>
        </div>
      </div>

    </div>
  );
}