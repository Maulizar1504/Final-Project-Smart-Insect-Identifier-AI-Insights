'use client';

import { useRef, useState } from 'react';
import ResultCard from '@/components/ResultCard';

export default function Home() {
  const [image, setImage]       = useState<File | null>(null);
  const [preview, setPreview]   = useState<string | null>(null);
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState<any>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    if (file.type && !file.type.startsWith('image/')) {
      alert('Hanya file gambar yang diperbolehkan (JPG, PNG, JPEG)');
      return;
    }
    setImage(file);
    setResult(null);
    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  const clearImage = () => {
    setImage(null);
    setPreview(null);
    setResult(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  const analyzeImage = async () => {
    if (!image) return;
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', image);

    try {
      const res = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        body:   formData,
      });

      const raw = await res.json();
      console.log("Response Mentah Backend:", raw); 

      if (!res.ok) throw new Error(raw.detail || 'Server error');

      // Ambil data prediksi utama dan tingkat confidence-nya
      const topClassName = raw.prediction?.class_name || raw.class_name || '';
      const topConfidence = raw.prediction?.confidence || raw.confidence || 0;

      // Mapping dengan fallback yang aman untuk komponen ResultCard Anda
      const data = {
        top_prediction: topClassName,
        predictions: raw.prediction?.top_k?.map((item: any) => ({
          class: item.class_name || item.class || '',
          prob: item.probability !== undefined ? item.probability : (item.confidence || item.prob || 0)
        })) || [
          {
            class: topClassName,
            prob: topConfidence,
          },
        ],
        ai_insight: raw.insights?.content || raw.insights || raw.ai_insight || ''
      };

      console.log("Data Hasil Mapping:", data);
      setResult(data);

    } catch (err: any) {
      alert(err.message || 'Backend tidak dapat dihubungi');
    } finally {
      setLoading(false);
    }
  }; // <-- Kurung kurawal penutup fungsi analyzeImage yang tadi hilang ada di sini

  return (
    <main
      className="min-h-screen flex justify-center py-12 px-4"
      style={{ background: 'var(--bg)', color: 'var(--text)' }}
    >

      {/* Atmospheric warm glow */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{ background: 'radial-gradient(ellipse 80% 40% at 50% 0%, rgba(212,146,26,0.07) 0%, transparent 100%)' }}
      />

      <div className="w-full max-w-3xl relative z-10">

        {/* ── Header ───────────────────────────── */}
        <header className="text-center mb-10">
          <div className="flex items-center justify-center gap-3 mb-3">
            <span className="block h-px w-8" style={{ background: 'var(--border)' }} />
            <span
              className="text-xs tracking-[0.3em] uppercase font-medium"
              style={{ color: 'var(--text-muted)' }}
            >
              AI Entomology
            </span>
            <span className="block h-px w-8" style={{ background: 'var(--border)' }} />
          </div>

          <h1 className="font-display text-5xl md:text-6xl font-bold tracking-tight">
            Lens<span style={{ color: 'var(--amber-light)' }}>Arthropoda</span>
          </h1>

          <p className="mt-3 text-sm tracking-wide" style={{ color: 'var(--text-muted)' }}>
            Smart Insect Identifier &amp; AI Insights
          </p>
        </header>

        {/* ── Upload Card ───────────────────────── */}
        <div
          className="rounded-2xl p-6 shadow-2xl"
          style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}
        >
          <input
            ref={inputRef}
            id="image-upload"
            type="file"
            accept="image/*"
            onChange={handleInputChange}
            className="hidden"
          />

          {/* Drop zone */}
          <label
            htmlFor="image-upload"
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className="relative w-full h-72 rounded-xl flex items-center justify-center cursor-pointer overflow-hidden transition-all duration-300 block"
            style={{
              border:     dragOver ? '2px dashed var(--amber-light)' : '2px dashed var(--border)',
              background: dragOver ? 'var(--amber-dim)' : 'transparent',
            }}
          >
            {preview ? (
              <>
                <img
                  src={preview}
                  alt="preview"
                  className="w-full h-full object-contain"
                />
                <div
                  className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-200"
                  style={{ background: 'rgba(0,0,0,0.6)' }}
                >
                  <span className="text-sm font-semibold" style={{ color: 'var(--amber-light)' }}>
                    Klik untuk ganti gambar
                  </span>
                </div>
              </>
            ) : (
              <div className="text-center select-none px-6">
                <div
                  className="w-14 h-14 mx-auto mb-4 rounded-full flex items-center justify-center"
                  style={{ background: 'var(--amber-dim)', border: '1px solid var(--border)' }}
                >
                  <svg
                    className="w-6 h-6"
                    fill="none" viewBox="0 0 24 24" stroke="currentColor"
                    style={{ color: 'var(--amber)' }}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <p className="font-semibold mb-1" style={{ color: 'var(--amber)' }}>
                  Klik atau seret gambar ke sini
                </p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  JPG · PNG · JPEG
                </p>
              </div>
            )}
          </label>

          {/* File info */}
          {image && (
            <div
              className="mt-3 flex items-center gap-2 text-sm px-1"
              style={{ color: 'var(--text-muted)' }}
            >
              <svg
                className="w-4 h-4 shrink-0"
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
                style={{ color: 'var(--amber)', opacity: 0.7 }}
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="truncate">{image.name}</span>
              <span className="ml-auto shrink-0 text-xs font-mono">
                {(image.size / 1024).toFixed(0)} KB
              </span>
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 mt-5">
            <button
              onClick={analyzeImage}
              disabled={!image || loading}
              className="flex-1 py-3 rounded-xl font-semibold text-sm transition-all duration-200"
              style={
                !image || loading
                  ? {
                      background: 'var(--surface-2)',
                      color:      'var(--text-muted)',
                      cursor:     'not-allowed',
                      border:     '1px solid var(--border)',
                    }
                  : {
                      background: 'var(--amber)',
                      color:      '#0c0a08',
                    }
              }
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10"
                      stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Menganalisis...
                </span>
              ) : 'Analisis Serangga'}
            </button>

            <button
              onClick={clearImage}
              className="px-5 rounded-xl text-sm font-medium transition-all duration-200"
              style={{
                background: 'var(--surface-2)',
                color:      'var(--text-muted)',
                border:     '1px solid var(--border)',
              }}
              onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--text)'; }}
              onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-muted)'; }}
            >
              Reset
            </button>
          </div>

        </div>

        {/* ── Result ───────────────────────────── */}
        {result && (
          <div className="mt-6 animate-fade-up">
            <ResultCard result={result} />
          </div>
        )}

      </div>
    </main>
  );
}