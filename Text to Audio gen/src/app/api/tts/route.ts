import { NextRequest, NextResponse } from 'next/server';
import { EdgeTTS } from 'edge-tts-universal';

// ── Voice map ─────────────────────────────────────────────────────────────────
const VOICE_MAP: Record<string, { male: string; female: string }> = {
    'en-GB': { female: 'en-GB-LibbyNeural',   male: 'en-GB-RyanNeural'     },
    'en-US': { female: 'en-US-AriaNeural',    male: 'en-US-GuyNeural'      },
    'en-AU': { female: 'en-AU-NatashaNeural', male: 'en-AU-WilliamNeural'  },
    'en-CA': { female: 'en-CA-ClaraNeural',   male: 'en-CA-LiamNeural'     },
    'en-IN': { female: 'en-IN-NeerjaNeural',  male: 'en-IN-PrabhatNeural'  },
    'en-NZ': { female: 'en-NZ-MollyNeural',   male: 'en-NZ-MitchellNeural' },
    'en-IE': { female: 'en-IE-EmilyNeural',   male: 'en-IE-ConnorNeural'   },
    'en-ZA': { female: 'en-ZA-LeahNeural',    male: 'en-ZA-LukasNeural'    },
};

// ── Generation adjustments ────────────────────────────────────────────────────
const GENERATION_ADJ = {
    child:  { pitch: '+12Hz', rateOffset: +6 },
    young:  { pitch: '+4Hz',  rateOffset: +3 },
    adult:  { pitch: '+0Hz',  rateOffset:  0 },
    senior: { pitch: '-6Hz',  rateOffset: -6 },
} as const;
type Generation = keyof typeof GENERATION_ADJ;

// ── Cambridge B2 profiles ─────────────────────────────────────────────────────
interface CambridgeProfile {
    gender: 'male' | 'female'; accent: string; generation: Generation;
    speed: number; pauseAfterLineMs: number; voiceOverride?: string;
}
const CAMBRIDGE_PROFILES: Record<string, CambridgeProfile> = {
    'rubric':      { gender:'female', accent:'en-GB', generation:'adult', speed:0.85, pauseAfterLineMs:0,   voiceOverride:'en-GB-SoniaNeural'  },
    'examiner':    { gender:'female', accent:'en-GB', generation:'adult', speed:0.85, pauseAfterLineMs:0,   voiceOverride:'en-GB-SoniaNeural'  },
    'narrator':    { gender:'female', accent:'en-GB', generation:'adult', speed:0.85, pauseAfterLineMs:0,   voiceOverride:'en-GB-SoniaNeural'  },
    'tom':         { gender:'male',   accent:'en-GB', generation:'adult', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-GB-RyanNeural'   },
    'lucy':        { gender:'female', accent:'en-GB', generation:'adult', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-GB-LibbyNeural'  },
    'boy':         { gender:'male',   accent:'en-GB', generation:'child', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-GB-RyanNeural'   },
    'woman':       { gender:'female', accent:'en-GB', generation:'adult', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-GB-LibbyNeural'  },
    'man':         { gender:'male',   accent:'en-GB', generation:'adult', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-GB-RyanNeural'   },
    'mike':        { gender:'male',   accent:'en-IE', generation:'young', speed:0.90, pauseAfterLineMs:400, voiceOverride:'en-IE-ConnorNeural' },
    'lisa':        { gender:'female', accent:'en-AU', generation:'young', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-AU-NatashaNeural'},
    'carlos':      { gender:'male',   accent:'en-GB', generation:'young', speed:0.95, pauseAfterLineMs:400, voiceOverride:'en-GB-ThomasNeural' },
    'interviewer': { gender:'female', accent:'en-GB', generation:'adult', speed:1.00, pauseAfterLineMs:400, voiceOverride:'en-GB-LibbyNeural'  },
    'sam':         { gender:'male',   accent:'en-GB', generation:'child', speed:1.00, pauseAfterLineMs:400, voiceOverride:'en-GB-RyanNeural'   },
};

// Part-speed defaults for unrecognised speakers
const PART_SPEEDS: Record<number, number> = { 1:0.95, 2:0.90, 3:0.95, 4:1.00 };

// ── Types ─────────────────────────────────────────────────────────────────────
interface SpeakerConfig {
    gender: 'male'|'female'; accent: string; generation: Generation;
    speed: number; pauseAfterLineMs: number; voiceOverride?: string;
}

type Segment =
    | { type:'speech'; speaker:string; text:string }
    | { type:'beep' }
    | { type:'pause'; durationMs:number };

// ── Transcript parser ─────────────────────────────────────────────────────────
// Accepts ALL of these formats (and more):
//   "A: text"                   single-letter (old format)
//   "Ram: text"                 plain name
//   "Tom (MAN): text"           Cambridge name+hint
//   "Speaker 1: text"           name with number
//   "RUBRIC: text"              all-caps name
//   "[BEEP]" / "BEEP]"         beep variants
//   "PAUSE 00'05\""             timed silence
function parseTranscript(text: string): { segments: Segment[]; speakers: string[] } {
    const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
    const segments: Segment[] = [];
    const speakerOrder: string[] = [];
    const speakerSet  = new Set<string>();
    let currentSpeaker = '';
    let currentPart    = 1;

    for (const line of lines) {
        // ── Combined [BEEP] PAUSE on one line ────────────────────────────────
        const beepPause = line.match(/^\[?BEEP\]?\s+PAUSE\s+(\d+)['']\s*(\d+)["""]?$/i);
        if (beepPause) {
            segments.push({ type:'beep' });
            segments.push({ type:'pause', durationMs:(+beepPause[1]*60 + +beepPause[2])*1000 });
            continue;
        }

        // ── Standalone PAUSE ──────────────────────────────────────────────────
        const pauseM = line.match(/^PAUSE\s+(\d+)['']\s*(\d+)["""]?$/i);
        if (pauseM) {
            segments.push({ type:'pause', durationMs:(+pauseM[1]*60 + +pauseM[2])*1000 });
            continue;
        }

        // ── BEEP (all bracket variants + *BEEP* + (BEEP)) ────────────────────
        if (/^\[?BEEP\]?$/i.test(line) || /^\*beep\*$/i.test(line) || /^\(beep\)$/i.test(line)) {
            segments.push({ type:'beep' });
            continue;
        }

        // ── Speaker line ──────────────────────────────────────────────────────
        // Accepts: single letter, multi-word name (with numbers in word 2+),
        // optional (TYPE) hint in parentheses, then colon.
        const m = line.match(
            /^([A-Za-z][A-Za-z0-9]*(?:\s[A-Za-z0-9]+){0,3})\s*(?:\([^)]*\))?\s*:\s*(.+)$/
        );
        if (m) {
            const speaker    = m[1].trim();
            const speechText = m[2].trim();

            if (!speakerSet.has(speaker)) { speakerSet.add(speaker); speakerOrder.push(speaker); }
            currentSpeaker = speaker;

            // Track which Cambridge part we are in (for speed defaults)
            const key = speaker.toLowerCase();
            if (key === 'rubric' || key === 'examiner' || key === 'narrator') {
                const pm = speechText.match(/\bPart\s+([1-4])\b/i);
                if (pm) currentPart = parseInt(pm[1]);
            }

            if (speechText) segments.push({ type:'speech', speaker, text:speechText });
            continue;
        }

        // ── Continuation (no colon prefix) ───────────────────────────────────
        if (currentSpeaker) {
            segments.push({ type:'speech', speaker:currentSpeaker, text:line });
        }
    }

    return { segments, speakers:speakerOrder };
}

// ── Audio helpers ─────────────────────────────────────────────────────────────
function getVoiceName(cfg: SpeakerConfig): string {
    if (cfg.voiceOverride) return cfg.voiceOverride;
    return (VOICE_MAP[cfg.accent] ?? VOICE_MAP['en-GB'])[cfg.gender];
}

function buildRate(speed: number, offset: number): string {
    const p = Math.round((speed - 1) * 100) + offset;
    return p >= 0 ? `+${p}%` : `${p}%`;
}

// MPEG2 Layer3, 24kHz, 48kbps, mono — 288 bytes = 24ms
const SILENT_FRAME = Buffer.from([0xFF,0xF3,0x64,0xC0, ...new Array(284).fill(0x00)]);
function silenceBuffer(ms: number): Buffer {
    const n = Math.max(1, Math.ceil(ms / 24));
    return Buffer.concat(Array.from({ length:n }, () => SILENT_FRAME));
}

async function generateBeepMp3(durationMs: number, frequency = 440): Promise<Buffer> {
    const { Mp3Encoder } = await import('@breezystack/lamejs');
    const sr   = 24000;
    const n    = Math.ceil(sr * durationMs / 1000);
    const fade = Math.ceil(sr * 0.03);
    const s    = new Int16Array(n);
    for (let i = 0; i < n; i++) {
        let a = 0.55 * 32767;
        if (i < fade)      a *= i / fade;
        else if (i > n-fade) a *= (n-i) / fade;
        s[i] = Math.round(a * Math.sin(2*Math.PI*frequency*i/sr));
    }
    const enc = new Mp3Encoder(1, sr, 48);
    const chunks: Buffer[] = [];
    for (let i = 0; i < n; i += 1152) {
        const pad = new Int16Array(1152); pad.set(s.subarray(i, i+1152));
        const b: Uint8Array = enc.encodeBuffer(pad);
        if (b.length) chunks.push(Buffer.from(b));
    }
    const tail: Uint8Array = enc.flush();
    if (tail.length) chunks.push(Buffer.from(tail));
    return Buffer.concat(chunks);
}

function trimTrailingSilence(audio: Buffer): Buffer {
    const F=288, SIDE=17; let end=audio.length;
    while (end >= F) {
        const fs = end-F;
        if (audio[fs] !== 0xFF || audio[fs+1] !== 0xF3) break;
        let silent = true;
        for (let i = fs+4+SIDE; i < end; i++) { if (audio[i]) { silent=false; break; } }
        if (silent) end=fs; else break;
    }
    return end < audio.length ? audio.subarray(0,end) : audio;
}

const sleep = (ms: number) => new Promise<void>(r => setTimeout(r, ms));

async function synthesizeLine(text: string, voice: string, rate: string, pitch: string): Promise<Buffer> {
    for (let attempt = 0; attempt < 3; attempt++) {
        if (attempt > 0) await sleep(200 * attempt);
        try {
            const tts    = new EdgeTTS(text, voice, { rate, pitch });
            const result = await tts.synthesize();
            const buf    = Buffer.from(await result.audio.arrayBuffer());
            if (buf.length > 200) return buf;
        } catch (err) { if (attempt === 2) throw err; }
    }
    throw new Error(`Failed to synthesize: "${text.substring(0, 60)}…"`);
}

// ── Route handler ─────────────────────────────────────────────────────────────
export async function POST(req: NextRequest) {
    try {
        const { transcript, speakers, filename = 'Listening_Test' } = await req.json() as {
            transcript: string;
            speakers:   Record<string, SpeakerConfig>;
            filename?:  string;
        };

        if (!transcript?.trim()) return NextResponse.json({ error:'Transcript is empty.' }, { status:400 });

        const { segments } = parseTranscript(transcript);
        if (!segments.some(s => s.type === 'speech'))
            return NextResponse.json({ error:'No speech lines found. Use format "Name: text".' }, { status:400 });

        // ── Parallel batch processing (3 concurrent) — ~3× faster than sequential ──
        const BATCH = 3;
        const STAGGER = 150; // ms between requests within a batch

        type Task = () => Promise<Buffer>;
        const tasks: Task[] = segments.map((seg, i) => async () => {
            if (seg.type === 'beep') {
                return Buffer.concat([await generateBeepMp3(700), silenceBuffer(100)]);
            }
            if (seg.type === 'pause') {
                return silenceBuffer(seg.durationMs);
            }
            // seg.type === 'speech'
            const cfg = speakers[seg.speaker];
            if (!cfg) return Buffer.alloc(0);

            const adj    = GENERATION_ADJ[cfg.generation] ?? GENERATION_ADJ.adult;
            const voice  = getVoiceName(cfg);
            const rate   = buildRate(cfg.speed, adj.rateOffset);
            const isLast = i === segments.length - 1;
            const raw    = await synthesizeLine(seg.text, voice, rate, adj.pitch);
            const audio  = isLast ? trimTrailingSilence(raw) : raw;
            const pause  = !isLast && cfg.pauseAfterLineMs > 0 ? silenceBuffer(cfg.pauseAfterLineMs) : null;
            return pause ? Buffer.concat([audio, pause]) : audio;
        });

        const buffers: Buffer[] = [];
        for (let i = 0; i < tasks.length; i += BATCH) {
            const batch = tasks.slice(i, Math.min(i+BATCH, tasks.length));
            const results = await Promise.all(
                batch.map((task, j) => new Promise<Buffer>((res, rej) =>
                    setTimeout(() => task().then(res).catch(rej), j * STAGGER)
                ))
            );
            buffers.push(...results);
            if (i + BATCH < tasks.length) await sleep(60);
        }

        const final = buffers.filter(b => b.length > 0);
        if (!final.length) return NextResponse.json({ error:'Nothing generated — check speaker names.' }, { status:400 });

        const safeName = filename.replace(/[^a-zA-Z0-9 _\-]/g,'').trim() || 'Listening_Test';

        return new NextResponse(Buffer.concat(final), {
            status: 200,
            headers: {
                'Content-Type':        'audio/mpeg',
                'Content-Disposition': `attachment; filename="${safeName}.mp3"`,
            },
        });
    } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'TTS generation failed';
        console.error('[TTS Error]', err);
        return NextResponse.json({ error:msg }, { status:500 });
    }
}
