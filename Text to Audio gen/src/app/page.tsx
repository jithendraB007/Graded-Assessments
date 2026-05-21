"use client";

import React, { useState, useMemo, useEffect, useCallback } from 'react';

// ── Types ─────────────────────────────────────────────────────────────────────
type Generation = 'child' | 'young' | 'adult' | 'senior';

interface SpeakerConfig {
    gender:           'male' | 'female';
    accent:           string;
    generation:       Generation;
    speed:            number;
    pauseAfterLineMs: number;
    voiceOverride?:   string;
}

interface SpeakerUIMeta extends SpeakerConfig {
    isCambridge: boolean;
    description: string;
    customising: boolean;
}

interface Segment {
    type:    'speech' | 'beep' | 'pause';
    speaker?: string;
    text?:   string;
}

// ── Cambridge B2 built-in profiles ───────────────────────────────────────────
const CAMBRIDGE_PROFILES: Record<string, {
    gender: 'male'|'female'; accent: string; generation: Generation;
    speed: number; pauseAfterLineMs: number; voiceOverride?: string;
    description: string;
}> = {
    'rubric':      { gender:'female', accent:'en-GB', generation:'adult', speed:0.85, pauseAfterLineMs:0,   voiceOverride:'en-GB-SoniaNeural',   description:'British RP · Examiner · 0.85×'           },
    'examiner':    { gender:'female', accent:'en-GB', generation:'adult', speed:0.85, pauseAfterLineMs:0,   voiceOverride:'en-GB-SoniaNeural',   description:'British RP · Examiner · 0.85×'           },
    'narrator':    { gender:'female', accent:'en-GB', generation:'adult', speed:0.85, pauseAfterLineMs:0,   voiceOverride:'en-GB-SoniaNeural',   description:'British RP · Narrator · 0.85×'           },
    'tom':         { gender:'male',   accent:'en-GB', generation:'adult', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-GB-RyanNeural',    description:'Southern British Male · Adult · 0.95×'   },
    'lucy':        { gender:'female', accent:'en-GB', generation:'adult', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-GB-LibbyNeural',   description:'Southern British Female · Adult · 0.95×' },
    'boy':         { gender:'male',   accent:'en-GB', generation:'child', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-GB-RyanNeural',    description:'Estuary English Male · Youth · 0.95×'    },
    'woman':       { gender:'female', accent:'en-GB', generation:'adult', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-GB-LibbyNeural',   description:'Northern British Female · Adult · 0.95×' },
    'man':         { gender:'male',   accent:'en-GB', generation:'adult', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-GB-RyanNeural',    description:'Southern British Male · Adult · 0.95×'   },
    'mike':        { gender:'male',   accent:'en-IE', generation:'young', speed:0.90, pauseAfterLineMs:400, voiceOverride:'en-IE-ConnorNeural',  description:'Irish English Male · Adult · 0.90×'       },
    'lisa':        { gender:'female', accent:'en-AU', generation:'young', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-AU-NatashaNeural', description:'Australian Female · Young Adult · 0.95×'  },
    'carlos':      { gender:'male',   accent:'en-GB', generation:'young', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-GB-ThomasNeural',  description:'Southern British Male · Teen · 0.95×'    },
    'interviewer': { gender:'female', accent:'en-GB', generation:'adult', speed:1.00, pauseAfterLineMs:400, voiceOverride:'en-GB-LibbyNeural',   description:'Southern British Female · Adult · 1.00×' },
    'sam':         { gender:'male',   accent:'en-GB', generation:'child', speed:1.00, pauseAfterLineMs:400, voiceOverride:'en-GB-RyanNeural',    description:'Scottish English Male · Youth · 1.00×'   },
};

const ACCENTS = [
    { id: 'en-GB', label: 'British English'       },
    { id: 'en-US', label: 'American English'      },
    { id: 'en-AU', label: 'Australian English'    },
    { id: 'en-CA', label: 'Canadian English'      },
    { id: 'en-NZ', label: 'New Zealand English'   },
    { id: 'en-IE', label: 'Irish English'         },
    { id: 'en-IN', label: 'Indian English'        },
    { id: 'en-ZA', label: 'South African English' },
];

const GENERATIONS: { id: Generation; label: string }[] = [
    { id: 'child',  label: 'Child'       },
    { id: 'young',  label: 'Young Adult' },
    { id: 'adult',  label: 'Adult'       },
    { id: 'senior', label: 'Senior'      },
];

const FALLBACK_POOL: Array<{ gender:'male'|'female'; accent: string }> = [
    { gender:'female', accent:'en-GB' },
    { gender:'male',   accent:'en-US' },
    { gender:'female', accent:'en-AU' },
    { gender:'male',   accent:'en-GB' },
    { gender:'female', accent:'en-CA' },
    { gender:'male',   accent:'en-AU' },
    { gender:'female', accent:'en-IN' },
    { gender:'male',   accent:'en-NZ' },
];

// ── Transcript parser ─────────────────────────────────────────────────────────
function parseTranscript(text: string) {
    const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
    const segments: Segment[]              = [];
    const speakerOrder: string[]           = [];
    const speakerHints: Record<string, string> = {};
    const speakerSet = new Set<string>();
    let cur = '';

    for (const line of lines) {
        if (/^\[?BEEP\]?\s+PAUSE\s+\d+['']\d+/i.test(line)) {
            segments.push({ type:'beep' }); segments.push({ type:'pause' }); continue;
        }
        if (/^PAUSE\s+\d+['']\d+/i.test(line)) { segments.push({ type:'pause' }); continue; }
        if (/^\[?BEEP\]?$/i.test(line) || /^\*beep\*$/i.test(line) || /^\(beep\)$/i.test(line)) {
            segments.push({ type:'beep' }); continue;
        }
        // Name (HINT): text  — accepts "Speaker 1:", "Tom (MAN):", "A:", "RUBRIC:", etc.
        const m = line.match(/^([A-Za-z][A-Za-z0-9]*(?:\s[A-Za-z0-9]+){0,3})\s*(?:\(([^)]*)\))?\s*:\s*(.+)$/);
        if (m) {
            const speaker = m[1].trim();
            const hint    = (m[2] ?? '').trim().toUpperCase();
            const speech  = m[3].trim();
            if (!speakerSet.has(speaker)) { speakerSet.add(speaker); speakerOrder.push(speaker); }
            if (hint && !speakerHints[speaker]) speakerHints[speaker] = hint;
            cur = speaker;
            if (speech) segments.push({ type:'speech', speaker, text:speech });
        } else if (cur) {
            segments.push({ type:'speech', speaker:cur, text:line });
        }
    }
    return { segments, speakers:speakerOrder, speakerHints };
}

function buildDefaultConfig(speaker: string, hint: string, fallbackIndex: number): SpeakerUIMeta {
    const profile = CAMBRIDGE_PROFILES[speaker.toLowerCase()];
    if (profile) return { ...profile, isCambridge:true, customising:false };

    let gender: 'male'|'female' = FALLBACK_POOL[fallbackIndex % FALLBACK_POOL.length].gender;
    let generation: Generation  = 'adult';
    const accent                = FALLBACK_POOL[fallbackIndex % FALLBACK_POOL.length].accent;

    if      (hint === 'MAN')   { gender = 'male';   generation = 'adult'; }
    else if (hint === 'WOMAN') { gender = 'female'; generation = 'adult'; }
    else if (hint === 'BOY')   { gender = 'male';   generation = 'child'; }
    else if (hint === 'GIRL')  { gender = 'female'; generation = 'young'; }

    return { gender, accent, generation, speed:0.95, pauseAfterLineMs:400,
             isCambridge:false, description:'', customising:false };
}

// ── App ───────────────────────────────────────────────────────────────────────
export default function Home() {
    const [transcript, setTranscript] = useState('');
    const [configs,    setConfigs]    = useState<Record<string, SpeakerUIMeta>>({});
    const [filename,   setFilename]   = useState('Listening_Test_1');
    const [generating, setGenerating] = useState(false);
    const [audioUrl,   setAudioUrl]   = useState<string | null>(null);
    const [statusMsg,  setStatusMsg]  = useState('');
    const [audioName,  setAudioName]  = useState('');

    const { speakers, segments, speakerHints } = useMemo(
        () => parseTranscript(transcript),
        [transcript],
    );

    const speechCount = segments.filter(s => s.type === 'speech').length;
    const beepCount   = segments.filter(s => s.type === 'beep').length;
    const pauseCount  = segments.filter(s => s.type === 'pause').length;

    // Auto-build configs as speakers are detected (preserves manual overrides)
    useEffect(() => {
        setConfigs(prev => {
            const next: Record<string, SpeakerUIMeta> = {};
            speakers.forEach((sp, i) => {
                next[sp] = prev[sp] ?? buildDefaultConfig(sp, speakerHints[sp] ?? '', i);
            });
            return next;
        });
    }, [speakers, speakerHints]);

    const updateConfig = useCallback((speaker: string, patch: Partial<SpeakerUIMeta>) => {
        setConfigs(prev => ({ ...prev, [speaker]: { ...prev[speaker], ...patch } }));
    }, []);

    const toggleCustomise = useCallback((speaker: string) => {
        setConfigs(prev => ({
            ...prev,
            [speaker]: { ...prev[speaker], customising: !prev[speaker].customising },
        }));
    }, []);

    const generateAudio = useCallback(async () => {
        if (!transcript.trim() || speechCount === 0) return;
        setGenerating(true);
        setAudioUrl(null);
        setStatusMsg('Generating with Microsoft Neural Voices — this may take 30–60 seconds…');
        try {
            const payload: Record<string, SpeakerConfig> = {};
            for (const [name, cfg] of Object.entries(configs)) {
                payload[name] = {
                    gender: cfg.gender, accent: cfg.accent, generation: cfg.generation,
                    speed: cfg.speed, pauseAfterLineMs: cfg.pauseAfterLineMs,
                    voiceOverride: cfg.voiceOverride,
                };
            }
            const res = await fetch('/api/tts', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ transcript, speakers: payload, filename }),
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({})) as { error?: string };
                throw new Error(err.error ?? `Server error ${res.status}`);
            }
            const blob = await res.blob();
            setAudioUrl(URL.createObjectURL(blob));
            setAudioName(filename.replace(/[^a-zA-Z0-9 _\-]/g, '').trim() || 'Listening_Test');
            setStatusMsg('');
        } catch (e: unknown) {
            alert('Generation failed: ' + (e instanceof Error ? e.message : String(e)));
            setStatusMsg('');
        } finally {
            setGenerating(false);
        }
    }, [transcript, configs, filename, speechCount]);

    const speedLabel = (s: number) =>
        s <= 0.7 ? 'Very Slow' : s <= 0.9 ? 'Slow' : s <= 1.1 ? 'Normal' : s <= 1.3 ? 'Fast' : 'Very Fast';

    return (
        <div>
            {/* ── Header ── */}
            <header className="app-header">
                <div>
                    <span className="app-logo">EduAudio</span>
                    <span className="app-logo-tagline">Cambridge B2 Listening Test Audio Generator</span>
                </div>
                <span style={{ fontSize:'0.75rem', color:'var(--text-secondary)' }}>
                    Microsoft Neural Voices · Free
                </span>
            </header>

            <div className="main">
                <div className="two-col">

                    {/* ════════ LEFT — Transcript ════════ */}
                    <div className="col-transcript">
                        <div className="card">
                            <div className="card-title">Paste Your Script</div>
                            <div className="card-subtitle">
                                Speakers, pauses and beeps are detected automatically as you type.
                            </div>

                            <div className="info-box">
                                <strong>Supported formats</strong><br />
                                <code>Rubric: There are four parts to the test.</code><br />
                                <code>Tom (MAN): Did you do anything nice?</code><br />
                                <code>PAUSE 00&apos;05&quot;</code> &nbsp;·&nbsp; <code>[BEEP]</code> &nbsp;·&nbsp;
                                <code>A: text</code> &nbsp;·&nbsp; <code>Speaker 1: text</code>
                            </div>

                            <div className="transcript-wrap">
                                <div className="transcript-toolbar">
                                    <span>{transcript.length} chars</span>
                                    <span>
                                        {speechCount > 0 ? `${speechCount} line${speechCount !== 1 ? 's' : ''}` : 'No speech detected'}
                                        {beepCount  > 0 ? ` · ${beepCount} beep${beepCount  > 1 ? 's' : ''}` : ''}
                                        {pauseCount > 0 ? ` · ${pauseCount} pause${pauseCount > 1 ? 's' : ''}` : ''}
                                    </span>
                                </div>
                                <textarea
                                    className="transcript-input"
                                    value={transcript}
                                    onChange={e => setTranscript(e.target.value)}
                                    placeholder={`Rubric: There are four parts to the test.\n\nPAUSE 00'05"\n\nTom (MAN): Did you do anything nice at the weekend?\nLucy (WOMAN): Yes! I went to the cinema.\n\n[BEEP]\n\nPAUSE 00'03"`}
                                    spellCheck
                                />
                            </div>

                            {speakers.length > 0 && (
                                <div className="detected-chips">
                                    <span className="chips-label">Detected:</span>
                                    {speakers.map(sp => (
                                        <span key={sp} className={`chip ${CAMBRIDGE_PROFILES[sp.toLowerCase()] ? 'chip-cambridge' : 'chip-speaker'}`}>
                                            {CAMBRIDGE_PROFILES[sp.toLowerCase()] ? '✓ ' : ''}{sp}
                                            {speakerHints[sp] ? <em> ({speakerHints[sp]})</em> : null}
                                        </span>
                                    ))}
                                    {beepCount  > 0 && <span className="chip chip-beep">🔔 {beepCount} beep{beepCount > 1 ? 's' : ''}</span>}
                                    {pauseCount > 0 && <span className="chip chip-pause">⏸ {pauseCount} pause{pauseCount > 1 ? 's' : ''}</span>}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* ════════ RIGHT — Speakers + Generate ════════ */}
                    <div className="col-side">

                        {/* Speakers panel */}
                        {speakers.length === 0 ? (
                            <div className="card empty-state">
                                <div className="empty-icon">🎤</div>
                                <div className="empty-title">Speakers appear here</div>
                                <div className="empty-sub">
                                    Paste your transcript on the left — speakers will be automatically detected and configured with the correct Cambridge B2 voices.
                                </div>
                            </div>
                        ) : (
                            <div className="card">
                                <div className="card-title">{speakers.length} Speaker{speakers.length !== 1 ? 's' : ''} Detected</div>
                                <div className="card-subtitle">
                                    Cambridge B2 profiles are auto-applied. Click ▼ to customise any voice.
                                </div>
                                <div className="speakers-stack">
                                    {speakers.map(sp => {
                                        const cfg = configs[sp];
                                        if (!cfg) return null;
                                        const accentLabel = ACCENTS.find(a => a.id === cfg.accent)?.label ?? cfg.accent;

                                        return (
                                            <div key={sp} className={`speaker-row${cfg.isCambridge ? ' speaker-row-cambridge' : ''}`}>
                                                <div className="speaker-row-header">
                                                    <div className="speaker-row-name">
                                                        🎤 <strong>{sp}</strong>
                                                        {cfg.isCambridge && (
                                                            <span className="cambridge-badge" style={{ marginLeft:'0.375rem' }}>Cambridge ✓</span>
                                                        )}
                                                    </div>
                                                    <button className="btn btn-ghost customise-btn-sm" onClick={() => toggleCustomise(sp)}>
                                                        {cfg.customising ? '▲' : '▼'}
                                                    </button>
                                                </div>
                                                <div className="speaker-row-desc">
                                                    {cfg.isCambridge
                                                        ? cfg.description
                                                        : `${cfg.gender === 'female' ? '♀ Female' : '♂ Male'} · ${accentLabel} · ${cfg.speed.toFixed(2)}×`
                                                    }
                                                </div>

                                                {cfg.customising && (
                                                    <div className="customise-panel">
                                                        {/* Gender */}
                                                        <div className="form-group">
                                                            <div className="form-label">Gender</div>
                                                            <div className="gender-toggle">
                                                                <button
                                                                    className={`gender-btn${cfg.gender === 'female' ? ' active-female' : ''}`}
                                                                    onClick={() => updateConfig(sp, { gender:'female', voiceOverride:undefined, isCambridge:false })}>
                                                                    ♀ Female
                                                                </button>
                                                                <button
                                                                    className={`gender-btn${cfg.gender === 'male' ? ' active-male' : ''}`}
                                                                    onClick={() => updateConfig(sp, { gender:'male', voiceOverride:undefined, isCambridge:false })}>
                                                                    ♂ Male
                                                                </button>
                                                            </div>
                                                        </div>
                                                        {/* Accent */}
                                                        <div className="form-group">
                                                            <label className="form-label">English Accent</label>
                                                            <select value={cfg.accent}
                                                                onChange={e => updateConfig(sp, { accent:e.target.value, voiceOverride:undefined, isCambridge:false })}>
                                                                {ACCENTS.map(a => <option key={a.id} value={a.id}>{a.label}</option>)}
                                                            </select>
                                                        </div>
                                                        {/* Age group */}
                                                        <div className="form-group">
                                                            <label className="form-label">Age Group</label>
                                                            <select value={cfg.generation}
                                                                onChange={e => updateConfig(sp, { generation:e.target.value as Generation, isCambridge:false })}>
                                                                {GENERATIONS.map(g => <option key={g.id} value={g.id}>{g.label}</option>)}
                                                            </select>
                                                        </div>
                                                        {/* Speed */}
                                                        <div className="slider-row">
                                                            <div className="form-label">
                                                                Speed — <strong>{speedLabel(cfg.speed)}</strong> ({cfg.speed.toFixed(2)}×)
                                                            </div>
                                                            <input type="range" min="0.5" max="1.5" step="0.05" value={cfg.speed}
                                                                onChange={e => updateConfig(sp, { speed:parseFloat(e.target.value), isCambridge:false })} />
                                                            <div className="slider-labels"><span>Slower</span><span>Normal</span><span>Faster</span></div>
                                                        </div>
                                                        {/* Pause */}
                                                        <div className="slider-row">
                                                            <div className="form-label">
                                                                Gap after line — <strong>{(cfg.pauseAfterLineMs/1000).toFixed(1)}s</strong>
                                                            </div>
                                                            <input type="range" min="0" max="1500" step="100" value={cfg.pauseAfterLineMs}
                                                                onChange={e => updateConfig(sp, { pauseAfterLineMs:parseInt(e.target.value), isCambridge:false })} />
                                                            <div className="slider-labels"><span>None</span><span>Short</span><span>Long</span></div>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Generate card */}
                        <div className="card generate-card">
                            <div className="form-group">
                                <label className="form-label">File Name</label>
                                <div className="filename-wrap">
                                    <input type="text" value={filename}
                                        onChange={e => setFilename(e.target.value)}
                                        placeholder="B2_Listening_Test_1"
                                        style={{ flex:1 }} />
                                    <span className="filename-ext">.mp3</span>
                                </div>
                            </div>

                            {statusMsg && (
                                <div className="status-msg"><span>⏳</span> {statusMsg}</div>
                            )}

                            {audioUrl && !generating && (
                                <div className="info-box" style={{ marginBottom:'0.75rem' }}>
                                    Audio ready — use the player below to listen, then download.
                                </div>
                            )}

                            <button
                                className="btn btn-success btn-lg"
                                style={{ width:'100%' }}
                                onClick={generateAudio}
                                disabled={speechCount === 0 || generating}
                            >
                                {generating
                                    ? '⏳ Generating…'
                                    : speechCount === 0
                                    ? 'Paste a transcript first'
                                    : '🎵 Generate Audio'
                                }
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* ── Sticky player bar ── */}
            {audioUrl && (
                <div className="player-bar">
                    <audio controls src={audioUrl} autoPlay style={{ flex:1, minWidth:0 }} />
                    <a href={audioUrl} download={`${audioName}.mp3`} style={{ flexShrink:0 }}>
                        <button className="btn btn-primary">⬇ Download {audioName}.mp3</button>
                    </a>
                </div>
            )}
        </div>
    );
}
