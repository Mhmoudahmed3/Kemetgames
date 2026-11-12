import { safeGetStorage, safeSetStorage } from '/js/utils.js?v=20261112';

/**
 * Zero-dependency Web Audio API sound effects synthesizer.
 */
class SoundEngine {
  constructor() {
    this.muted = safeGetStorage('blackout_muted', '0') === '1';
    this.ctx = null;
    this._noiseBuffer = null;
  }

  _ensureCtx() {
    if (this.muted) return null;
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return null;
      this.ctx = new AudioCtx();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }
    return this.ctx;
  }

  _getNoiseBuffer(ctx) {
    if (this._noiseBuffer && this._noiseBuffer.sampleRate === ctx.sampleRate) {
      return this._noiseBuffer;
    }
    const sampleRate = ctx.sampleRate;
    const frameCount = Math.max(1, Math.floor(sampleRate * 1.0));
    const buffer = ctx.createBuffer(1, frameCount, sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < frameCount; i++) {
      data[i] = Math.random() * 2 - 1;
    }
    this._noiseBuffer = buffer;
    return buffer;
  }

  isMuted() {
    return this.muted;
  }

  toggleMute() {
    this.muted = !this.muted;
    safeSetStorage('blackout_muted', this.muted ? '1' : '0');
    return this.muted;
  }

  _tone({ freq = 440, endFreq = null, type = 'square', duration = 0.08, gain = 0.12, delay = 0 } = {}) {
    const ctx = this._ensureCtx();
    if (!ctx) return;
    const now = ctx.currentTime + delay;
    const osc = ctx.createOscillator();
    const amp = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, now);
    if (endFreq !== null) {
      osc.frequency.exponentialRampToValueAtTime(Math.max(20, endFreq), now + duration);
    }
    amp.gain.setValueAtTime(gain, now);
    amp.gain.exponentialRampToValueAtTime(0.001, now + duration);
    osc.connect(amp);
    amp.connect(ctx.destination);
    osc.onended = () => {
      try { osc.disconnect(); } catch {}
      try { amp.disconnect(); } catch {}
    };
    osc.start(now);
    osc.stop(now + duration);
  }

  _noise(duration = 0.08, filterFreq = 1800, gain = 0.12, delay = 0) {
    const ctx = this._ensureCtx();
    if (!ctx) return;
    const buffer = this._getNoiseBuffer(ctx);
    const src = ctx.createBufferSource();
    src.buffer = buffer;
    if (duration > buffer.duration) {
      src.loop = true;
    }

    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = filterFreq;

    const amp = ctx.createGain();
    const now = ctx.currentTime + delay;
    amp.gain.setValueAtTime(gain, now);
    amp.gain.exponentialRampToValueAtTime(0.001, now + duration);

    src.connect(filter);
    filter.connect(amp);
    amp.connect(ctx.destination);
    src.onended = () => {
      try { src.disconnect(); } catch {}
      try { filter.disconnect(); } catch {}
      try { amp.disconnect(); } catch {}
    };
    src.start(now);
    src.stop(now + duration);
  }

  click() {
    this._tone({ freq: 580, endFreq: 220, type: 'triangle', duration: 0.04, gain: 0.08 });
  }

  tick() {
    this._tone({ freq: 1040, type: 'sine', duration: 0.045, gain: 0.07 });
  }

  card() {
    this._noise(0.06, 2600, 0.14);
  }

  dice() {
    this._noise(0.05, 1300, 0.14, 0.0);
    this._noise(0.05, 1700, 0.14, 0.07);
    this._noise(0.06, 1500, 0.12, 0.14);
  }

  chessMove() {
    this._tone({ freq: 210, endFreq: 90, type: 'triangle', duration: 0.06, gain: 0.16 });
    this._noise(0.03, 900, 0.1, 0.0);
  }

  capture() {
    this._tone({ freq: 170, endFreq: 55, type: 'sawtooth', duration: 0.12, gain: 0.18 });
  }

  skru() {
    this._tone({ freq: 620, type: 'square', duration: 0.12, gain: 0.12, delay: 0.0 });
    this._tone({ freq: 440, type: 'square', duration: 0.16, gain: 0.12, delay: 0.13 });
  }

  win() {
    [523.25, 659.25, 783.99, 1046.5].forEach((f, idx) => {
      this._tone({ freq: f, type: 'triangle', duration: 0.18, gain: 0.13, delay: idx * 0.09 });
    });
  }

  error() {
    this._tone({ freq: 220, endFreq: 110, type: 'sawtooth', duration: 0.18, gain: 0.11 });
  }
}

export const sound = new SoundEngine();
