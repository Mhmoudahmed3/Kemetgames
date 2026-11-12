/**
 * Shared security, resilient storage, and participant helpers for Blackout Arcade.
 */

export const ASSET_VERSION = '20261112';

const HTML_ESCAPE_MAP = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
};

export function escapeHtml(str) {
  return String(str ?? '').replace(/[&<>"']/g, (ch) => HTML_ESCAPE_MAP[ch]);
}

function getStorageArea(kind = 'local') {
  try {
    return kind === 'session' ? window.sessionStorage : window.localStorage;
  } catch {
    return null;
  }
}

export function safeGetStorage(key, fallback = null, kind = 'local') {
  try {
    const area = getStorageArea(kind);
    if (!area) return fallback;
    const val = area.getItem(key);
    return val === null ? fallback : val;
  } catch {
    return fallback;
  }
}

export function safeSetStorage(key, value, kind = 'local') {
  try {
    const area = getStorageArea(kind);
    if (!area) return false;
    area.setItem(key, String(value));
    return true;
  } catch {
    return false;
  }
}

export function getActivePlayers(players) {
  return Array.isArray(players)
    ? players.filter((p) => p && p.role !== 'spectator')
    : [];
}
