import {
  ASSET_VERSION,
  escapeHtml,
  getActivePlayers,
  safeGetStorage,
  safeSetStorage,
} from '/js/utils.js?v=20261112';
import { sound } from '/js/sound.js?v=20261112';
import { GAME_HUB_META, renderGameHeroArt, renderActivityThumb } from '/js/game_hub_data.js?v=20261112';
import { loadWorldAtlas, createInteractiveMap } from '/js/world_map.js?v=20261112';

const DEFAULT_ACCENT_HEX = '#E5484D';

const ACCENT_PRESETS = [
  { id: 'crimson', name: 'Crimson Glow', hex: '#E5484D' },
  { id: 'violet', name: 'Dusk Violet', hex: '#6B62F2' },
  { id: 'cobalt', name: 'Cobalt Ice', hex: '#3B82F6' },
  { id: 'amber', name: 'Sunset Amber', hex: '#F59E0B' },
  { id: 'emerald', name: 'Emerald Mist', hex: '#10B981' },
  { id: 'rose', name: 'Rose Quartz', hex: '#F43F5E' },
  { id: 'mono', name: 'Pure Mono', hex: '#EDEDED' },
];

const GLASS_PRESETS = {
  subtle: { blur: '10px', sat: '130%' },
  liquid: { blur: '20px', sat: '165%' },
  deep: { blur: '32px', sat: '195%' },
};

const GAME_HAZARD_ICONS = {
  explore:
    '<svg viewBox="0 0 32 32" fill="none"><circle cx="16" cy="16" r="14" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.35"/><circle cx="16" cy="16" r="11" stroke="currentColor" stroke-width="0.8" stroke-dasharray="1.5 2.5" stroke-opacity="0.5"/><line x1="16" y1="1" x2="16" y2="4" stroke="var(--accent)" stroke-width="1.5" stroke-linecap="round"/><line x1="16" y1="28" x2="16" y2="31" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-opacity="0.6"/><line x1="1" y1="16" x2="4" y2="16" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-opacity="0.6"/><line x1="28" y1="16" x2="31" y2="16" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-opacity="0.6"/><polygon points="16,6 18,14 26,16 18,18 16,26 14,18 6,16 14,14" fill="currentColor" fill-opacity="0.12"/><g transform="translate(16,16) rotate(-28) translate(-16,-16)"><polygon points="16,4 23,26 16,21" fill="currentColor"/><polygon points="16,4 9,26 16,21" fill="currentColor" fill-opacity="0.45"/><polygon points="16,8 20,22 16,19" fill="var(--accent)" fill-opacity="0.9"/></g><circle cx="16" cy="16" r="2.5" fill="var(--accent)"/><circle cx="16" cy="16" r="1" fill="#fff"/></svg>',
  snake:
    '<svg viewBox="0 0 32 32" fill="none"><g stroke="currentColor" stroke-width="0.5" stroke-opacity="0.18"><line x1="4" y1="8" x2="28" y2="8"/><line x1="4" y1="16" x2="28" y2="16"/><line x1="4" y1="24" x2="28" y2="24"/><line x1="8" y1="4" x2="8" y2="28"/><line x1="16" y1="4" x2="16" y2="28"/><line x1="24" y1="4" x2="24" y2="28"/></g><path d="M6 25 H18 A4 4 0 0 0 22 21 V13 A4 4 0 0 0 18 9 H14 A4 4 0 0 1 10 5" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.85"/><circle cx="8" cy="25" r="1.2" fill="var(--accent)"/><circle cx="14" cy="25" r="1.2" fill="var(--accent)"/><circle cx="22" cy="17" r="1.2" fill="var(--accent)"/><circle cx="18" cy="9" r="1.2" fill="var(--accent)"/><path d="M10 6.5 L6 4 L10 1.5 Z" fill="currentColor"/><circle cx="8.5" cy="3.5" r="0.8" fill="var(--accent)"/><path d="M5 4 H2 M2 4 L0.5 2.5 M2 4 L0.5 5.5" stroke="var(--accent)" stroke-width="0.9" stroke-linecap="round"/><circle cx="6" cy="25" r="1.8" fill="currentColor" fill-opacity="0.5"/><circle cx="24" cy="23" r="3.2" fill="var(--accent)"/><circle cx="24" cy="23" r="5" stroke="var(--accent)" stroke-width="0.8" stroke-dasharray="1.5 1.5" stroke-opacity="0.7"/><path d="M24 19.8 C25 18.5 26.5 18.5 27 19" stroke="currentColor" stroke-width="0.8" stroke-linecap="round"/></svg>',
  minesweeper:
    '<svg viewBox="0 0 32 32" fill="none"><circle cx="16" cy="16" r="14.5" stroke="var(--accent)" stroke-width="0.8" stroke-dasharray="2 3" stroke-opacity="0.45"/><circle cx="16" cy="16" r="12" stroke="currentColor" stroke-width="0.6" stroke-opacity="0.25"/><line x1="16" y1="2" x2="16" y2="7" stroke="var(--color-bone)" stroke-width="2.4" stroke-linecap="round"/><circle cx="16" cy="2" r="1.6" fill="var(--accent)"/><circle cx="16" cy="2" r="0.6" fill="#fff"/><line x1="16" y1="25" x2="16" y2="30" stroke="var(--color-bone)" stroke-width="2.4" stroke-linecap="round"/><circle cx="16" cy="30" r="1.6" fill="var(--accent)"/><circle cx="16" cy="30" r="0.6" fill="#fff"/><line x1="2" y1="16" x2="7" y2="16" stroke="var(--color-bone)" stroke-width="2.4" stroke-linecap="round"/><circle cx="2" cy="16" r="1.6" fill="var(--accent)"/><circle cx="2" cy="16" r="0.6" fill="#fff"/><line x1="25" y1="16" x2="30" y2="16" stroke="var(--color-bone)" stroke-width="2.4" stroke-linecap="round"/><circle cx="30" cy="16" r="1.6" fill="var(--accent)"/><circle cx="30" cy="16" r="0.6" fill="#fff"/><line x1="6" y1="6" x2="9.8" y2="9.8" stroke="var(--color-bone)" stroke-width="2.2" stroke-linecap="round"/><circle cx="5" cy="5" r="1.6" fill="var(--accent)"/><circle cx="5" cy="5" r="0.6" fill="#fff"/><line x1="22.2" y1="22.2" x2="26" y2="26" stroke="var(--color-bone)" stroke-width="2.2" stroke-linecap="round"/><circle cx="27" cy="27" r="1.6" fill="var(--accent)"/><circle cx="27" cy="27" r="0.6" fill="#fff"/><line x1="26" y1="6" x2="22.2" y2="9.8" stroke="var(--color-bone)" stroke-width="2.2" stroke-linecap="round"/><circle cx="27" cy="5" r="1.6" fill="var(--accent)"/><circle cx="27" cy="5" r="0.6" fill="#fff"/><line x1="9.8" y1="22.2" x2="6" y2="26" stroke="var(--color-bone)" stroke-width="2.2" stroke-linecap="round"/><circle cx="5" cy="27" r="1.6" fill="var(--accent)"/><circle cx="5" cy="27" r="0.6" fill="#fff"/><circle cx="16" cy="16" r="8.5" fill="#18181B" stroke="var(--accent)" stroke-width="1.8"/><circle cx="16" cy="16" r="7" stroke="rgba(255,255,255,0.25)" stroke-width="0.8"/><circle cx="16" cy="10" r="0.8" fill="#fff" opacity="0.6"/><circle cx="21" cy="12" r="0.8" fill="#fff" opacity="0.6"/><circle cx="22" cy="16" r="0.8" fill="#fff" opacity="0.6"/><circle cx="21" cy="20" r="0.8" fill="#fff" opacity="0.6"/><circle cx="16" cy="22" r="0.8" fill="#fff" opacity="0.6"/><circle cx="11" cy="20" r="0.8" fill="#fff" opacity="0.6"/><circle cx="10" cy="16" r="0.8" fill="#fff" opacity="0.6"/><circle cx="11" cy="12" r="0.8" fill="#fff" opacity="0.6"/><circle cx="16" cy="16" r="4.2" fill="var(--accent)" fill-opacity="0.88"/><circle cx="14" cy="14" r="1.2" fill="#fff"/><polygon points="16,13.5 18,17.5 14,17.5" fill="#101012"/><circle cx="16" cy="16.5" r="0.6" fill="#fff"/></svg>',
  chess:
    '<svg viewBox="0 0 32 32" fill="none"><g transform="translate(1,0)"><g opacity="0.35" stroke="currentColor" stroke-width="0.8" fill="currentColor"><path d="M4 25h9v-2h-1l-1-9h2v-4H4v4h2l-1 9H4z"/><path d="M4 10h2.5v2H8v-2h2v2h1.5v-2H13v3H4z"/></g><g transform="translate(5,2) scale(0.6)"><path d="M22 10C32.5 11 38.5 18 38 39H15C15 30 25 32.5 23 18" fill="rgba(18,18,24,0.9)" stroke="currentColor" stroke-width="1.8"/><path d="M24 18c.38 2.91-5.55 7.37-8 9-3 2-2.82 4.34-5 4-1.04-.94 1.41-3.04 0-3-1 0 .19 1.23-1 2-1 0-4.003 1-4-4 0-2 6-12 6-12s1.89-1.9 2-3.5c-.73-.994-.5-2-.5-3 1-1 3 2.5 3 2.5h2s.78-1.992 2.5-3c1 0 1 3 1 3" fill="rgba(18,18,24,0.9)" stroke="currentColor" stroke-width="1.8"/><circle cx="14.5" cy="15.5" r="1.5" fill="var(--accent)"/><circle cx="9.5" cy="25.5" r="1" fill="var(--accent)"/><path d="M24.5 10.5c-.2 1.4.3 2.8 1.3 3.8M27.6 12c-.2 1.4.3 2.8 1.3 3.8M30.7 13.6c-.2 1.4.3 2.8 1.3 3.8" stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round"/><path d="M9 39h27c0-2-1-3-2-3H11c-1 0-2 1-2 3z" fill="currentColor"/></g></g><rect x="3" y="27" width="26" height="2.5" rx="1" fill="currentColor"/><rect x="5" y="28.5" width="22" height="1" rx="0.5" fill="var(--accent)"/></svg>',
  backgammon:
    '<svg viewBox="0 0 32 32" fill="none"><rect x="2" y="2" width="28" height="28" rx="3" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.4"/><line x1="16" y1="2" x2="16" y2="30" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.5"/><polygon points="4,3 7,13 10,3" fill="var(--accent)" fill-opacity="0.7"/><polygon points="10,3 13,13 16,3" fill="currentColor" fill-opacity="0.3"/><polygon points="16,3 19,13 22,3" fill="var(--accent)" fill-opacity="0.7"/><polygon points="22,3 25,13 28,3" fill="currentColor" fill-opacity="0.3"/><polygon points="4,29 7,19 10,29" fill="currentColor" fill-opacity="0.3"/><polygon points="10,29 13,19 16,29" fill="var(--accent)" fill-opacity="0.7"/><circle cx="7" cy="6" r="2.4" fill="currentColor" stroke="var(--accent)" stroke-width="0.8"/><circle cx="7" cy="10" r="2.4" fill="currentColor" stroke="var(--accent)" stroke-width="0.8"/><circle cx="13" cy="26" r="2.4" fill="var(--accent)" stroke="currentColor" stroke-width="0.8"/><g transform="translate(17,15)"><rect x="0" y="0" width="11" height="11" rx="2" fill="currentColor" stroke="var(--accent)" stroke-width="1"/><circle cx="2.8" cy="2.8" r="0.9" fill="var(--accent)"/><circle cx="8.2" cy="2.8" r="0.9" fill="var(--accent)"/><circle cx="5.5" cy="5.5" r="0.9" fill="var(--accent)"/><circle cx="2.8" cy="8.2" r="0.9" fill="var(--accent)"/><circle cx="8.2" cy="8.2" r="0.9" fill="var(--accent)"/></g></svg>',
  dominoes:
    '<svg viewBox="0 0 32 32" fill="none"><rect x="4" y="8" width="12" height="21" rx="2" fill="currentColor" fill-opacity="0.25" stroke="currentColor" stroke-width="1" stroke-opacity="0.4" transform="rotate(-14 10 18)"/><g transform="translate(11,2) rotate(12)"><rect x="0" y="0" width="13" height="25" rx="2.5" fill="currentColor" stroke="var(--accent)" stroke-width="1.2"/><line x1="1" y1="12.5" x2="12" y2="12.5" stroke="#101012" stroke-width="1.2"/><circle cx="6.5" cy="12.5" r="1.3" fill="var(--accent)"/><circle cx="6.5" cy="12.5" r="0.5" fill="#fff"/><circle cx="3.2" cy="3.2" r="1" fill="#101012"/><circle cx="9.8" cy="3.2" r="1" fill="#101012"/><circle cx="6.5" cy="6.3" r="1" fill="#101012"/><circle cx="3.2" cy="9.4" r="1" fill="#101012"/><circle cx="9.8" cy="9.4" r="1" fill="#101012"/><circle cx="3.2" cy="15.5" r="1" fill="#101012"/><circle cx="9.8" cy="15.5" r="1" fill="#101012"/><circle cx="3.2" cy="21.8" r="1" fill="#101012"/><circle cx="9.8" cy="21.8" r="1" fill="#101012"/></g></svg>',
  ludo:
    '<svg viewBox="0 0 32 32" fill="none"><rect x="2" y="2" width="28" height="28" rx="4" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.45"/><rect x="3" y="3" width="9" height="9" rx="2" fill="var(--accent)" fill-opacity="0.65"/><circle cx="7.5" cy="7.5" r="2" fill="currentColor"/><rect x="20" y="3" width="9" height="9" rx="2" fill="currentColor" fill-opacity="0.25"/><circle cx="24.5" cy="7.5" r="2" fill="var(--accent)"/><rect x="3" y="20" width="9" height="9" rx="2" fill="currentColor" fill-opacity="0.25"/><circle cx="7.5" cy="24.5" r="2" fill="var(--accent)"/><rect x="20" y="20" width="9" height="9" rx="2" fill="var(--accent)" fill-opacity="0.65"/><circle cx="24.5" cy="24.5" r="2" fill="currentColor"/><polygon points="12,12 16,16 12,20" fill="var(--accent)"/><polygon points="20,12 16,16 20,20" fill="currentColor" fill-opacity="0.8"/><polygon points="12,12 16,16 20,12" fill="currentColor" fill-opacity="0.5"/><polygon points="12,20 16,16 20,20" fill="var(--accent)" fill-opacity="0.5"/><g transform="translate(16,16)"><circle cx="0" cy="-3.5" r="2.2" fill="#fff" stroke="var(--accent)" stroke-width="0.8"/><path d="M-2,-1 C-2,-1 -3,3 -3.5,4 H3.5 C3,3 2,-1 2,-1 Z" fill="var(--accent)"/><ellipse cx="0" cy="4" rx="4" ry="1.2" fill="currentColor"/></g></svg>',
  skru:
    '<svg viewBox="0 0 32 32" fill="none"><g transform="translate(5,4) rotate(-16)"><rect x="0" y="0" width="14" height="21" rx="2.5" fill="currentColor" fill-opacity="0.25" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/><circle cx="7" cy="10.5" r="3" fill="none" stroke="currentColor" stroke-width="0.8" stroke-dasharray="1.5 1"/></g><g transform="translate(9,3) rotate(-2)"><rect x="0" y="0" width="14" height="21" rx="2.5" fill="currentColor" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/><path d="M3 10.5 C4.5 8 9.5 8 11 10.5 C9.5 13 4.5 13 3 10.5 Z" fill="none" stroke="var(--accent)" stroke-width="0.9"/><circle cx="7" cy="10.5" r="1.5" fill="var(--accent)"/></g><g transform="translate(14,4) rotate(12)"><rect x="0" y="0" width="15" height="22" rx="2.5" fill="var(--accent)" stroke="#fff" stroke-width="1.2"/><rect x="1.5" y="1.5" width="12" height="19" rx="1.5" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="0.6"/><path d="M5 5.5 L6 4 L7.5 5.5 L9 4 L10 5.5 H5 Z" fill="#fff"/><ellipse cx="7.5" cy="11.5" rx="3.5" ry="4.5" fill="none" stroke="#fff" stroke-width="2.2"/><text x="3" y="5" fill="#fff" font-family="\'DM Sans\', sans-serif" font-weight="700" font-size="3.5" text-anchor="middle">0</text><text x="12" y="19" fill="#fff" font-family="\'DM Sans\', sans-serif" font-weight="700" font-size="3.5" text-anchor="middle">0</text></g></svg>',
  uno:
    '<svg viewBox="0 0 32 32" fill="none"><g transform="translate(4,4) rotate(-14)"><rect x="0" y="0" width="15" height="22" rx="3" fill="#101012" stroke="currentColor" stroke-width="1.2"/><ellipse cx="7.5" cy="11" rx="4.5" ry="7" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="2 1.5" opacity="0.6" transform="rotate(22 7.5 11)"/><text x="7.5" y="13" fill="currentColor" font-family="\'DM Sans\', sans-serif" font-weight="800" font-size="4.5" text-anchor="middle" transform="rotate(22 7.5 11)">+4</text></g><g transform="translate(13,3) rotate(8)"><rect x="0" y="0" width="16" height="23" rx="3" fill="var(--accent)" stroke="#fff" stroke-width="1.2"/><g transform="rotate(22 8 11.5)"><ellipse cx="8" cy="11.5" rx="5.2" ry="7.8" fill="#101012" stroke="rgba(255,255,255,0.4)" stroke-width="0.8"/><path d="M8 11.5 L8 4.2 A5.2 7.8 0 0 1 12.8 11.5 Z" fill="#E5484D"/><path d="M8 11.5 L12.8 11.5 A5.2 7.8 0 0 1 8 18.8 Z" fill="#3B82F6"/><path d="M8 11.5 L8 18.8 A5.2 7.8 0 0 1 3.2 11.5 Z" fill="#10B981"/><path d="M8 11.5 L3.2 11.5 A5.2 7.8 0 0 1 8 4.2 Z" fill="#F59E0B"/><circle cx="8" cy="11.5" r="2" fill="#fff"/><circle cx="8" cy="11.5" r="1.2" fill="#101012"/></g><text x="3.2" y="5.2" fill="#fff" font-family="\'DM Sans\', sans-serif" font-weight="800" font-size="4" text-anchor="middle">+4</text><text x="12.8" y="20.8" fill="#fff" font-family="\'DM Sans\', sans-serif" font-weight="800" font-size="4" text-anchor="middle">+4</text></g></svg>',
  qa_trivia:
    '<svg viewBox="0 0 32 32" fill="none"><circle cx="16" cy="15" r="11" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.35"/><ellipse cx="16" cy="15" rx="5.5" ry="11" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.45"/><ellipse cx="16" cy="15" rx="11" ry="4.5" stroke="currentColor" stroke-width="0.8" stroke-dasharray="2 1.5" stroke-opacity="0.4"/><path d="M6 24 C8 26 12 27 16 27 C20 27 24 26 26 24" stroke="var(--accent)" stroke-width="1.5" stroke-linecap="round"/><line x1="16" y1="27" x2="16" y2="30" stroke="var(--accent)" stroke-width="1.5" stroke-linecap="round"/><circle cx="16" cy="30.5" r="1.2" fill="var(--accent)"/><g transform="translate(25,6)"><polygon points="0,-3.5 0.8,-0.8 3.5,0 0.8,0.8 0,3.5 -0.8,0.8 -3.5,0 -0.8,-0.8" fill="var(--accent)"/></g><path d="M12.5 10.5 C12.5 7.8 14.2 6 16.5 6 C18.8 6 20.5 7.5 20.5 9.5 C20.5 11.5 19 12.8 17.5 14 C16.5 14.8 16 15.8 16 17.5" stroke="#101012" stroke-width="4.2" stroke-linecap="round"/><path d="M12.5 10.5 C12.5 7.8 14.2 6 16.5 6 C18.8 6 20.5 7.5 20.5 9.5 C20.5 11.5 19 12.8 17.5 14 C16.5 14.8 16 15.8 16 17.5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><circle cx="16" cy="21.5" r="2.2" fill="#101012"/><circle cx="16" cy="21.5" r="1.5" fill="var(--accent)"/></svg>',
  globe:
    '<svg viewBox="0 0 32 32" fill="none"><circle cx="16" cy="16" r="13" stroke="currentColor" stroke-width="1.4" stroke-opacity="0.35"/><circle cx="16" cy="16" r="14.5" stroke="var(--accent)" stroke-width="0.8" stroke-dasharray="2 2" stroke-opacity="0.6"/><ellipse cx="16" cy="16" rx="5.5" ry="13" stroke="currentColor" stroke-width="0.9" stroke-opacity="0.3"/><line x1="3" y1="16" x2="29" y2="16" stroke="currentColor" stroke-width="1" stroke-dasharray="2 1.5" stroke-opacity="0.5"/><ellipse cx="16" cy="10" rx="11" ry="3.5" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.25"/><ellipse cx="16" cy="22" rx="11" ry="3.5" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.25"/><path d="M7 11 C8 9 10 9 11 12 C11.5 14 10 16 11 18 C11.5 19 12.5 20 12 22 C11 23 9.5 21 8.5 18 C8 16 6.5 13 7 11 Z" fill="currentColor" fill-opacity="0.75"/><path d="M17 8 C19 7 21 8 21 10 C20 12 18 12 18.5 14 C19 16 22 17 21 21 C20 23 18 24 17 21 C16 19 16 15 17 12 Z" fill="currentColor" fill-opacity="0.75"/><path d="M10 14 Q16 7 23 12" stroke="var(--accent)" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="1.5 1.5"/><g transform="translate(23,12)"><circle cx="0" cy="0" r="3" stroke="var(--accent)" stroke-width="0.8"/><circle cx="0" cy="0" r="1.5" fill="var(--accent)"/><path d="M0 -5 L0 -3 M0 3 L0 5 M-5 0 L-3 0 M3 0 L5 0" stroke="var(--accent)" stroke-width="0.8"/></g></svg>',
  monopoly:
    '<svg viewBox="0 0 32 32" fill="none"><g transform="translate(14,3) rotate(8)"><rect x="0" y="0" width="14" height="20" rx="2" fill="currentColor" fill-opacity="0.2" stroke="currentColor" stroke-width="1"/><rect x="1" y="1" width="12" height="5" rx="1" fill="var(--accent)"/><polygon points="7,2 4.5,4 9.5,4" fill="#fff"/><rect x="5" y="4" width="4" height="2" fill="#fff"/><line x1="3" y1="8.5" x2="11" y2="8.5" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/><line x1="3" y1="11" x2="11" y2="11" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/><line x1="4" y1="13.5" x2="10" y2="13.5" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/></g><g transform="translate(3,10) rotate(-6)"><path d="M4 14 L5 4 H15 L16 14 Z" fill="currentColor" stroke="#101012" stroke-width="0.8"/><rect x="4.8" y="11" width="10.4" height="3" fill="var(--accent)"/><ellipse cx="10" cy="14.5" rx="9" ry="2.8" fill="currentColor" stroke="#101012" stroke-width="0.8"/><ellipse cx="10" cy="14" rx="7" ry="1.6" fill="var(--accent)" fill-opacity="0.3"/></g><g transform="translate(20,20)"><circle cx="5" cy="5" r="5.5" fill="var(--accent)" stroke="#fff" stroke-width="1"/><text x="5" y="8" fill="#fff" font-family="\'DM Sans\', sans-serif" font-weight="800" font-size="7.5" text-anchor="middle">$</text></g></svg>',
  tic_tac_toe:
    '<svg viewBox="0 0 32 32" fill="none">' +
    '<g stroke="currentColor" stroke-width="1" stroke-opacity="0.35" stroke-linecap="round">' +
    '<line x1="11" y1="4" x2="11" y2="28"/><line x1="21" y1="4" x2="21" y2="28"/>' +
    '<line x1="4" y1="11" x2="28" y2="11"/><line x1="4" y1="21" x2="28" y2="21"/>' +
    '</g>' +
    '<g stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round">' +
    '<line x1="6.5" y1="6.5" x2="9.5" y2="9.5"/><line x1="9.5" y1="6.5" x2="6.5" y2="9.5"/>' +
    '<line x1="22.5" y1="22.5" x2="25.5" y2="25.5"/><line x1="25.5" y1="22.5" x2="22.5" y2="25.5"/>' +
    '</g>' +
    '<circle cx="16" cy="16" r="3.2" fill="none" stroke="#fff" stroke-width="2"/>' +
    '<circle cx="24" cy="8" r="2.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-opacity="0.6"/>' +
    '<line x1="4.5" y1="4.5" x2="27.5" y2="27.5" stroke="var(--accent)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="2 1.5"/>' +
    '</svg>',
  rock_paper_scissors:
    '<svg viewBox="0 0 32 32" fill="none">' +
    '<g transform="translate(6, 6)">' +
    '<circle cx="10" cy="10" r="9" stroke="var(--accent)" stroke-width="1.2" stroke-dasharray="3 2" opacity="0.5"/>' +
    '<path d="M4 14V8C4 6.8 5 6 6 6C7 6 8 6.8 8 8V12M8 9C8 7.8 9 7 10 7C11 7 12 7.8 12 9V14M12 11C12 9.8 13 9 14 9C15 9 16 9.8 16 11V15" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>' +
    '<circle cx="15" cy="5" r="2.5" fill="var(--accent)"/>' +
    '</g>' +
    '</svg>',
  connect4:
    '<svg viewBox="0 0 32 32" fill="none">' +
    '<rect x="3" y="5" width="26" height="22" rx="3" fill="#141416" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.4"/>' +
    '<circle cx="8" cy="11" r="2.2" fill="#ff4034"/>' +
    '<circle cx="13.3" cy="11" r="2.2" fill="#facc15"/>' +
    '<circle cx="18.6" cy="11" r="2.2" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.3"/>' +
    '<circle cx="24" cy="11" r="2.2" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.3"/>' +
    '<circle cx="8" cy="16" r="2.2" fill="#facc15"/>' +
    '<circle cx="13.3" cy="16" r="2.2" fill="#ff4034"/>' +
    '<circle cx="18.6" cy="16" r="2.2" fill="#ff4034"/>' +
    '<circle cx="24" cy="16" r="2.2" fill="#facc15"/>' +
    '<circle cx="8" cy="21" r="2.2" fill="#ff4034"/>' +
    '<circle cx="13.3" cy="21" r="2.2" fill="#ff4034"/>' +
    '<circle cx="18.6" cy="21" r="2.2" fill="#facc15"/>' +
    '<circle cx="24" cy="21" r="2.2" fill="#ff4034"/>' +
    '<line x1="6" y1="23" x2="26" y2="9" stroke="#ff4034" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="2 1.5"/>' +
    '</svg>',
  playing_cards:
    '<svg viewBox="0 0 32 32" fill="none">' +
    '<rect x="4" y="6" width="14" height="20" rx="2.5" fill="#141418" stroke="currentColor" stroke-width="1.2" transform="rotate(-12 11 16)"/>' +
    '<rect x="13" y="5" width="15" height="21" rx="2.5" fill="#1e1e26" stroke="var(--accent)" stroke-width="1.4"/>' +
    '<path d="M20.5 11 C20 9 17 11 17 13.5 C17 15 18.5 16 19.5 16.5 V18 H21.5 V16.5 C22.5 16 24 15 24 13.5 C24 11 21 9 20.5 11 Z" fill="var(--accent)"/>' +
    '</svg>',
};

const GAME_SETTINGS_SCHEMA = {
  minesweeper: [
    { key: 'difficulty', label: 'DIFFICULTY', options: ['easy', 'mid', 'hard', 'custom'] },
  ],
  snake: [
    { key: 'difficulty', label: 'DIFFICULTY', options: ['easy', 'mid', 'hard'] },
    { key: 'duration', label: 'RACE CLOCK (SEC)', options: ['60', '90', '120'] },
  ],
  chess: [
    { key: 'difficulty', label: 'AI DIFFICULTY', options: ['easy', 'mid', 'hard'] },
    { key: 'time_control', label: 'CLOCK (MIN)', options: ['3+2', '5+0', '10+0'] },
  ],
  backgammon: [
    { key: 'difficulty', label: 'AI DIFFICULTY', options: ['easy', 'mid', 'hard'] },
    { key: 'mode', label: 'TAWLA MODE', options: ['classic', 'tawla_31', 'mahbosa'] },
  ],
  dominoes: [
    { key: 'difficulty', label: 'AI DIFFICULTY', options: ['easy', 'mid', 'hard'] },
    { key: 'target_score', label: 'TARGET POINTS', options: ['50', '100', '150'] },
  ],
  ludo: [
    { key: 'difficulty', label: 'AI DIFFICULTY', options: ['easy', 'mid', 'hard'] },
  ],
  skru: [
    { key: 'difficulty', label: 'AI DIFFICULTY', options: ['easy', 'mid', 'hard'] },
  ],
  uno: [
    { key: 'difficulty', label: 'AI DIFFICULTY', options: ['easy', 'mid', 'hard'] },
  ],
  qa_trivia: [
    { key: 'difficulty', label: 'DIFFICULTY', options: ['easy', 'mid', 'hard'] },
    {
      key: 'category',
      label: 'CATEGORY',
      options: ['All', 'Atlas', 'Flags', 'War', 'History', 'Science', 'Logic & Pattern IQ', 'General Knowledge', 'Tech & Pop Culture'],
    },
    { key: 'rounds', label: 'QUESTIONS', options: ['8', '10', '12', '15'] },
  ],
  globe: [
    { key: 'difficulty', label: 'DIFFICULTY', options: ['easy', 'mid', 'hard'] },
    { key: 'mode', label: 'GAMEPLAY MODE', options: ['mix', 'name', 'flag', 'hint', 'borders_between'] },
    { key: 'rounds', label: 'ROUNDS', options: ['6', '8', '12', '16'] },
  ],
  monopoly: [
    { key: 'difficulty', label: 'DIFFICULTY', options: ['easy', 'mid', 'hard'] },
  ],
  tic_tac_toe: [
    { key: 'mode', label: 'GAME MODE', options: ['classic', 'misere', 'extended_4x4', 'extended_5x5', 'ultimate'] },
    { key: 'difficulty', label: 'AI DIFFICULTY', options: ['easy', 'mid', 'hard'] },
    { key: 'first_player', label: 'FIRST MOVE', options: ['x', 'o', 'random'] },
    { key: 'grid_size', label: 'GRID SIZE', options: ['3', '4', '5'] },
  ],
  rock_paper_scissors: [
    { key: 'mode', label: 'GAME MODE', options: ['classic', 'lizard_spock'] },
    { key: 'format', label: 'MATCH FORMAT', options: ['bo3', 'bo5', 'endless'] },
    { key: 'difficulty', label: 'AI DIFFICULTY', options: ['easy', 'mid', 'hard'] },
  ],
  connect4: [
    { key: 'mode', label: 'GAME MODE', options: ['classic', 'pop_out', 'five_in_a_row', 'blitz'] },
    { key: 'difficulty', label: 'AI DIFFICULTY', options: ['easy', 'mid', 'hard'] },
    { key: 'blitz_time', label: 'BLITZ TIME (SEC)', options: ['5', '7', '10'] },
  ],
  playing_cards: [
    { key: 'mode', label: 'GAME MODE', options: ['blackjack', 'war', 'memory', 'high_low'] },
    { key: 'difficulty', label: 'AI DIFFICULTY', options: ['easy', 'mid', 'hard'] },
  ],
};

function getOrCreateClientId() {
  let cid = safeGetStorage('blackout_client_id', '', 'session');
  if (!cid) {
    cid = (crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}_${Math.random().toString(36).slice(2, 10)}`);
    safeSetStorage('blackout_client_id', cid, 'session');
  }
  return cid;
}

class BroadcastApp {
  constructor() {
    this.clientId = getOrCreateClientId();
    this.sessionSecret = safeGetStorage('blackout_session_secret', '', 'session') || '';
    this.playerName = safeGetStorage('blackout_player_name', '') || '';
    this.lastPlayedGame = safeGetStorage('blackout_last_game', 'chess') || 'chess';
    this.accentColor = safeGetStorage('blackout_accent_color', DEFAULT_ACCENT_HEX) || DEFAULT_ACCENT_HEX;
    this.glassIntensity = safeGetStorage('blackout_glass_intensity', 'liquid') || 'liquid';
    this.ws = null;
    this.reconnectTimer = null;
    this.catalog = [];
    this.openRooms = [];
    this.leaderboard = {};
    this.selectedGameType = 'explore';
    this.selectedDifficultyByGame = this._loadDifficultyMap();
    this.selectedQaCategory = safeGetStorage('blackout_qa_category', 'All') || 'All';
    this.joinModalFilterGame = null;
    this.currentView = 'entry';
    this.currentRoom = null;
    this.activeGameModule = null;
    this.activeGameType = null;
    this.publicState = null;
    this.privateState = {};
    this.players = [];
    this.helpPinned = false;
    this.commsOpen = false;
    this._hasUnreadComms = false;
    this._seenChatKey = '';
    this._lastEventsSig = '';
    this._lastChatSig = '';
    this._serverPlayerName = '';
    this._encyLoading = false;
    this._lastModalTrigger = null;
    this._bunkerSchemaKey = '';
    this._bunkerMinesTimer = null;
    this.toastTimer = null;
    this._diffPulseTimer = null;
    this._railSignature = '';
    this.pregameSetup = {
      selectedModeIndex: 0,
      matchupType: 'ai',
      playerCount: 1,
      minPlayers: 1,
      maxPlayers: 1,
    };

    this._cacheDom();
    this._initPersonalization();
    this._bindEvents();
    this._updateMuteButtons();
    this._setWsStatus(false);
    this._startClock();
    if (this.playerName) {
      this.dom.playerNameInput.value = this.playerName;
    }
    this._connectWS();
  }

  _cacheDom() {
    this.dom = {
      viewEntry: document.getElementById('view-entry'),
      viewLobby: document.getElementById('view-lobby'),
      viewArena: document.getElementById('view-arena'),
      toast: document.getElementById('toast-banner'),
      dynamicFavicon: document.getElementById('dynamic-favicon'),
      wsStatusDot: document.getElementById('ws-status-dot'),
      wsStatusEntry: document.getElementById('ws-status-entry'),
      topbarWsStatus: document.getElementById('topbar-ws-status'),
      hudWsStatus: document.getElementById('hud-ws-status'),
      entryForm: document.getElementById('entry-form'),
      playerNameInput: document.getElementById('player-name-input'),
      entryAccentSwatches: document.getElementById('entry-accent-swatches'),
      btnEntrySettings: document.getElementById('btn-entry-settings'),
      lobbyCallsign: document.getElementById('lobby-callsign-badge'),
      avatarInitial: document.getElementById('ps5-avatar-initial'),
      btnChangeName: document.getElementById('btn-change-name'),
      btnCloseQuickJoin: document.getElementById('btn-close-quickjoin'),
      modalQuickJoin: document.getElementById('modal-quickjoin'),
      modalJoinTitle: document.getElementById('modal-join-title'),
      modalJoinRoomsLabel: document.getElementById('modal-join-rooms-label'),
      modalOpenRooms: document.getElementById('modal-open-rooms'),
      modalJoinForm: document.getElementById('modal-join-form'),
      modalCodeInput: document.getElementById('modal-code-input'),
      btnJoinSubmit: document.getElementById('btn-join-submit'),
      btnOpenSettings: document.getElementById('btn-open-settings'),
      btnArenaSettings: document.getElementById('btn-arena-settings'),
      btnOpenLeaderboard: document.getElementById('btn-open-leaderboard'),
      btnOpenEncyclopedia: document.getElementById('btn-open-encyclopedia'),
      modalEncyclopedia: document.getElementById('modal-encyclopedia'),
      btnCloseEncyclopedia: document.getElementById('btn-close-encyclopedia'),
      encySearch: document.getElementById('ency-search'),
      encyContinentTabs: document.getElementById('ency-continent-tabs'),
      encyList: document.getElementById('ency-list'),
      encyMapHost: document.getElementById('ency-map-host'),
      encyDossier: document.getElementById('ency-dossier'),
      ps5Clock: document.getElementById('ps5-clock'),
      tabGames: document.getElementById('tab-games'),
      ps5GameRail: document.getElementById('ps5-game-rail'),
      ps5HeroArt: document.getElementById('ps5-hero-art'),
      ps5HeroMeta: document.getElementById('ps5-hero-meta'),
      ps5HeroTitle: document.getElementById('ps5-hero-title'),
      ps5HeroDesc: document.getElementById('ps5-hero-desc'),
      difficultyWrap: document.getElementById('ps5-difficulty-wrap'),
      diffPills: document.getElementById('ps5-diff-pills'),
      diffBtnCustom: document.getElementById('ps5-diff-btn-custom'),
      minesCustomRow: document.getElementById('ps5-mines-custom-row'),
      msInputWidth: document.getElementById('ms-input-width'),
      msInputHeight: document.getElementById('ms-input-height'),
      msInputBooms: document.getElementById('ms-input-booms'),
      qaCategoryRow: document.getElementById('ps5-qa-category-row'),
      qaCatPills: document.getElementById('ps5-qa-cat-pills'),
      difficultyHint: document.getElementById('ps5-difficulty-hint'),
      pregameSetupPanel: document.getElementById('pregame-setup-panel'),
      pregameMatchupRow: document.getElementById('pregame-matchup-row'),
      pregameMatchupPills: document.getElementById('pregame-matchup-pills'),
      btnMatchupAi: document.getElementById('btn-matchup-ai'),
      btnMatchupHost: document.getElementById('btn-matchup-host'),
      pregamePlayerCountRow: document.getElementById('pregame-player-count-row'),
      pregamePlayerRangeBadge: document.getElementById('pregame-player-range-badge'),
      btnPlayerCountDec: document.getElementById('btn-player-count-dec'),
      pregamePlayerCountVal: document.getElementById('pregame-player-count-val'),
      btnPlayerCountInc: document.getElementById('btn-player-count-inc'),
      btnPregameLaunch: document.getElementById('btn-pregame-launch'),
      btnHeroSolo: document.getElementById('btn-hero-solo'),
      btnHeroHost: document.getElementById('btn-hero-host'),
      btnHeroJoin: document.getElementById('btn-hero-join'),
      ps5ActivityStrip: document.getElementById('ps5-activity-strip'),
      ps5ControlsLine: document.getElementById('ps5-controls-line'),
      ps5HelpCards: document.getElementById('ps5-help-cards'),
      ps5GameRooms: document.getElementById('ps5-game-rooms'),
      ps5GameRecords: document.getElementById('ps5-game-records'),
      btnLeaveRoom: document.getElementById('btn-leave-room'),
      hudRoomCode: document.getElementById('hud-room-code'),
      btnCopyCode: document.getElementById('btn-copy-code'),
      hudGameTitle: document.getElementById('hud-game-title'),
      hudTurnIndicator: document.getElementById('hud-turn-indicator'),
      arenaSpectatorBadge: document.getElementById('arena-spectator-badge'),
      hudPlayersStrip: document.getElementById('hud-players-strip'),
      btnArenaMute: document.getElementById('btn-arena-mute'),
      btnPinHelp: document.getElementById('btn-pin-help'),
      btnUnpinHelp: document.getElementById('btn-unpin-help'),
      btnToggleComms: document.getElementById('btn-toggle-comms'),
      commsUnreadDot: document.getElementById('comms-unread-dot'),
      arenaCommsDrawer: document.getElementById('arena-comms-drawer'),
      btnCloseComms: document.getElementById('btn-close-comms'),
      arenaEventsList: document.getElementById('arena-events-list'),
      arenaChatList: document.getElementById('arena-chat-list'),
      arenaChatForm: document.getElementById('arena-chat-form'),
      arenaChatInput: document.getElementById('arena-chat-input'),
      pipHelpPanel: document.getElementById('pip-help-panel'),
      pipHelpBody: document.getElementById('pip-help-body'),
      waitingBunker: document.getElementById('waiting-bunker'),
      bunkerGameHeading: document.getElementById('bunker-game-heading'),
      bunkerRulesNote: document.getElementById('bunker-rules-note'),
      bunkerRoster: document.getElementById('bunker-roster'),
      bunkerSettings: document.getElementById('bunker-settings-panel'),
      bunkerMinesCustomRow: document.getElementById('bunker-mines-custom-row'),
      bunkerMsWidth: document.getElementById('bunker-ms-width'),
      bunkerMsHeight: document.getElementById('bunker-ms-height'),
      bunkerMsBooms: document.getElementById('bunker-ms-booms'),
      bunkerHostControls: document.getElementById('bunker-host-controls'),
      bunkerBotControls: document.getElementById('bunker-bot-controls'),
      btnAddBot: document.getElementById('btn-add-bot'),
      btnRemoveBot: document.getElementById('btn-remove-bot'),
      btnStartMatch: document.getElementById('btn-start-match'),
      bunkerGuestWait: document.getElementById('bunker-guest-wait'),
      gameStage: document.getElementById('game-stage'),
      modalSettings: document.getElementById('modal-settings'),
      btnCloseSettings: document.getElementById('btn-close-settings'),
      settingsPresetSwatches: document.getElementById('settings-preset-swatches'),
      settingsColorPicker: document.getElementById('settings-color-picker'),
      settingsColorHex: document.getElementById('settings-color-hex'),
      btnResetAccent: document.getElementById('btn-reset-accent'),
      settingsGlassPills: document.getElementById('settings-glass-pills'),
      btnSettingsMute: document.getElementById('btn-settings-mute'),
      btnSettingsRename: document.getElementById('btn-settings-rename'),
      modalGameover: document.getElementById('modal-gameover'),
      gameoverHeadline: document.getElementById('gameover-headline'),
      gameoverReason: document.getElementById('gameover-reason'),
      gameoverStandings: document.getElementById('gameover-standings'),
      btnRematch: document.getElementById('btn-rematch'),
      btnGameoverLobby: document.getElementById('btn-gameover-lobby'),
      modalLeaderboard: document.getElementById('modal-leaderboard'),
      btnCloseLeaderboard: document.getElementById('btn-close-leaderboard'),
      leaderboardTabs: document.getElementById('leaderboard-tabs'),
      leaderboardTableWrap: document.getElementById('leaderboard-table-wrap'),
      modalRename: document.getElementById('modal-rename'),
      renameForm: document.getElementById('rename-form'),
      renameInput: document.getElementById('rename-input'),
      btnCancelRename: document.getElementById('btn-cancel-rename'),
      modalChessEditor: document.getElementById('modal-chess-custom-editor'),
      btnCloseChessEditor: document.getElementById('btn-close-chess-editor'),
      chessEditorGrid: document.getElementById('chess-editor-grid'),
      chessPaletteWhite: document.getElementById('chess-palette-white'),
      chessPaletteBlack: document.getElementById('chess-palette-black'),
      btnChessBrushErase: document.getElementById('btn-chess-brush-erase'),
      btnChessPresetStd: document.getElementById('btn-chess-preset-std'),
      btnChessPresetKq: document.getElementById('btn-chess-preset-kq'),
      btnChessPresetClear: document.getElementById('btn-chess-preset-clear'),
      chessEditorStatus: document.getElementById('chess-editor-status'),
      btnLaunchCustomChess: document.getElementById('btn-launch-custom-chess'),
      btnHostCustomChess: document.getElementById('btn-host-custom-chess'),
    };
  }

  _normalizeHex(raw) {
    if (typeof raw !== 'string') return null;
    const s = raw.trim();
    const match = /^#?([0-9a-fA-F]{6})$/.exec(s);
    return match ? `#${match[1].toUpperCase()}` : null;
  }

  _initPersonalization() {
    this._renderSwatchControls();
    this._applyAccentColor(this.accentColor, false);
    this._applyGlassIntensity(this.glassIntensity, false);
  }

  _renderSwatchControls() {
    const buildMiniRow = (container) => {
      if (!container) return;
      container.innerHTML = '';
      ACCENT_PRESETS.slice(0, 5).forEach((preset) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `mini-swatch-btn swatch-${preset.id}`;
        btn.dataset.hex = preset.hex;
        btn.title = `${preset.name} (${preset.hex})`;
        btn.setAttribute('aria-label', preset.name);
        btn.addEventListener('click', () => {
          sound.tick();
          this._applyAccentColor(preset.hex, true);
        });
        container.appendChild(btn);
      });
    };

    buildMiniRow(this.dom.entryAccentSwatches);

    if (this.dom.settingsPresetSwatches) {
      this.dom.settingsPresetSwatches.innerHTML = '';
      ACCENT_PRESETS.forEach((preset) => {
        const card = document.createElement('button');
        card.type = 'button';
        card.className = 'settings-swatch-card';
        card.dataset.hex = preset.hex;
        const dot = document.createElement('span');
        dot.className = `swatch-preview-dot swatch-${preset.id}`;
        const label = document.createElement('span');
        label.textContent = preset.name;
        card.append(dot, label);
        card.addEventListener('click', () => {
          sound.click();
          this._applyAccentColor(preset.hex, true);
        });
        this.dom.settingsPresetSwatches.appendChild(card);
      });
    }
  }

  _applyAccentColor(rawHex, persist = true) {
    const hex = this._normalizeHex(rawHex) || DEFAULT_ACCENT_HEX;
    this.accentColor = hex;
    if (persist) {
      safeSetStorage('blackout_accent_color', hex);
    }

    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const srgbLinear = (c) => {
      const s = c / 255;
      return s <= 0.04045 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    };
    const lum = 0.2126 * srgbLinear(r) + 0.7152 * srgbLinear(g) + 0.0722 * srgbLinear(b);
    // Contrast with white: (1.0 + 0.05) / (lum + 0.05) >= 4.5  ==>  lum <= 0.1833
    const contrast = lum <= 0.1833 ? '#FFFFFF' : '#0A0A0A';

    const root = document.documentElement.style;
    root.setProperty('--accent', hex);
    root.setProperty('--accent-rgb', `${r}, ${g}, ${b}`);
    root.setProperty('--accent-subtle', `rgba(${r}, ${g}, ${b}, 0.09)`);
    root.setProperty('--accent-soft', `rgba(${r}, ${g}, ${b}, 0.18)`);
    root.setProperty('--accent-mid', `rgba(${r}, ${g}, ${b}, 0.42)`);
    root.setProperty('--accent-glow', `rgba(${r}, ${g}, ${b}, 0.565)`);
    root.setProperty('--accent-contrast', contrast);

    if (this.dom.dynamicFavicon) {
      const enc = encodeURIComponent(hex);
      this.dom.dynamicFavicon.href = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect width='24' height='24' rx='6' fill='%23161616'/%3E%3Ccircle cx='12' cy='12' r='6' fill='${enc}'/%3E%3C/svg%3E`;
    }

    if (this.dom.settingsColorPicker) this.dom.settingsColorPicker.value = hex.toLowerCase();
    if (this.dom.settingsColorHex) this.dom.settingsColorHex.value = hex;

    document.querySelectorAll('[data-hex]').forEach((el) => {
      el.classList.toggle('active', el.dataset.hex === hex);
    });
  }

  _applyGlassIntensity(level, persist = true) {
    const preset = GLASS_PRESETS[level] || GLASS_PRESETS.liquid;
    this.glassIntensity = GLASS_PRESETS[level] ? level : 'liquid';
    if (persist) {
      safeSetStorage('blackout_glass_intensity', this.glassIntensity);
    }
    const root = document.documentElement.style;
    root.setProperty('--glass-blur', preset.blur);
    root.setProperty('--glass-sat', preset.sat);

    if (this.dom.settingsGlassPills) {
      this.dom.settingsGlassPills.querySelectorAll('[data-glass]').forEach((btn) => {
        btn.classList.toggle('active', btn.dataset.glass === this.glassIntensity);
      });
    }
  }

  _getAllModals() {
    return [
      this.dom.modalSettings,
      this.dom.modalEncyclopedia,
      this.dom.modalQuickJoin,
      this.dom.modalLeaderboard,
      this.dom.modalRename,
      this.dom.modalChessEditor,
      this.dom.modalGameover,
    ].filter(Boolean);
  }

  _getClosableModals() {
    return [
      this.dom.modalSettings,
      this.dom.modalEncyclopedia,
      this.dom.modalQuickJoin,
      this.dom.modalLeaderboard,
      this.dom.modalRename,
      this.dom.modalChessEditor,
    ].filter(Boolean);
  }

  _getOpenModals() {
    return this._getAllModals().filter((m) => !m.classList.contains('hidden'));
  }

  _getFocusableInModal(modalEl) {
    if (!modalEl) return [];
    return Array.from(
      modalEl.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
    ).filter((el) => {
      if (el.disabled || el.hasAttribute('disabled') || el.type === 'hidden') return false;
      if (el.classList.contains('hidden')) return false;
      let cur = el;
      while (cur && cur !== modalEl) {
        if (cur.classList?.contains('hidden')) return false;
        cur = cur.parentElement;
      }
      return true;
    });
  }

  _openModal(modalEl, focusTarget = null) {
    if (!modalEl) return;
    const active = document.activeElement;
    if (active && !this._getAllModals().some((m) => m.contains(active))) {
      this._lastModalTrigger = active;
    }
    modalEl.classList.remove('hidden');
    requestAnimationFrame(() => {
      if (modalEl.classList.contains('hidden')) return;
      const target =
        focusTarget && !focusTarget.disabled && modalEl.contains(focusTarget)
          ? focusTarget
          : this._getFocusableInModal(modalEl)[0];
      if (target && typeof target.focus === 'function') {
        target.focus();
      }
    });
  }

  _closeModal(modalEl, { restoreFocus = true } = {}) {
    if (!modalEl || modalEl.classList.contains('hidden')) return;
    modalEl.classList.add('hidden');
    if (modalEl === this.dom.modalEncyclopedia) {
      this._encyMapCtrl?.destroy();
      this._encyMapCtrl = null;
    }
    if (restoreFocus && this._getOpenModals().length === 0) {
      const trigger = this._lastModalTrigger;
      this._lastModalTrigger = null;
      if (trigger && typeof trigger.focus === 'function' && document.contains(trigger)) {
        trigger.focus();
      }
    }
  }

  _openSettingsModal() {
    this._openModal(this.dom.modalSettings, this.dom.btnCloseSettings);
  }

  async _openEncyclopedia(initialCode = null) {
    if (this._encyLoading) return;
    this._openModal(this.dom.modalEncyclopedia, this.dom.encySearch);
    if (!this._encyContinent) this._encyContinent = 'All';

    if (!this._encyAtlas) {
      this._encyLoading = true;
      try {
        this._encyAtlas = await loadWorldAtlas();
      } catch {
        this._toast('Failed to load World Country Atlas.', true);
        this._closeModal(this.dom.modalEncyclopedia);
        return;
      } finally {
        this._encyLoading = false;
      }
    }

    if (this.dom.modalEncyclopedia.classList.contains('hidden')) {
      return;
    }

    if (!this._encyMapCtrl && this.dom.encyMapHost) {
      this._encyMapCtrl = createInteractiveMap(this.dom.encyMapHost, this._encyAtlas, {
        width: 540,
        height: 270,
        initialProjection: 'globe',
        showAllHoverNames: true,
        onCountryClick: (country) => {
          sound.click();
          this._selectEncyclopediaCountry(country.code);
        },
      });
    }

    this._renderEncyclopediaList();
    const targetCode = initialCode || this._encySelectedCode || 'EG';
    this._selectEncyclopediaCountry(targetCode);
  }

  _renderEncyclopediaList() {
    if (!this._encyAtlas) return;
    const query = (this.dom.encySearch?.value || '').trim().toLowerCase();
    const cont = this._encyContinent || 'All';
    const items = this._encyAtlas.countryList.filter((c) => {
      if (cont !== 'All' && c.continent !== cont) return false;
      if (!query) return true;
      return (
        c.name.toLowerCase().includes(query) ||
        c.capital.toLowerCase().includes(query) ||
        c.code.toLowerCase().includes(query) ||
        c.subregion.toLowerCase().includes(query)
      );
    });

    this.dom.encyList.innerHTML = '';
    if (!items.length) {
      this.dom.encyList.innerHTML = '<p class="empty-ticker-msg">No matching countries found.</p>';
      return;
    }

    const frag = document.createDocumentFragment();
    for (const c of items) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.dataset.code = c.code;
      btn.className = `ency-row ${c.code === this._encySelectedCode ? 'active' : ''}`;
      btn.innerHTML = `
        <img src="${escapeHtml(c.flag_svg)}" alt="${escapeHtml(c.name)}" class="ency-row-flag" />
        <div class="ency-row-meta">
          <strong>${escapeHtml(c.name)}</strong>
          <span>${escapeHtml(c.capital)} · ${escapeHtml(c.subregion)}</span>
        </div>
        <span class="ency-row-pop">${escapeHtml(c.population_label)}</span>
      `;
      btn.addEventListener('click', () => {
        sound.click();
        this._selectEncyclopediaCountry(c.code);
      });
      frag.appendChild(btn);
    }
    this.dom.encyList.appendChild(frag);
  }

  _selectEncyclopediaCountry(code) {
    if (!this._encyAtlas) return;
    const c = this._encyAtlas.countriesByCode[code] || this._encyAtlas.countryList[0];
    if (!c) return;
    this._encySelectedCode = c.code;

    this.dom.encyList?.querySelectorAll('.ency-row').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.code === c.code);
    });

    if (this._encyMapCtrl) {
      this._encyMapCtrl.setStyles({
        [c.code]: {
          fill: 'var(--accent)',
          stroke: '#FFFFFF',
          strokeWidth: 2,
          label: c.name,
          sublabel: `${c.capital} · Pop ${c.population_label}`,
        },
      });
      this._encyMapCtrl.flyTo(c.lat, c.lng, 1.02);
    }

    const latStr = `${Math.abs(c.lat).toFixed(1)}°${c.lat >= 0 ? 'N' : 'S'}`;
    const lngStr = `${Math.abs(c.lng).toFixed(1)}°${c.lng >= 0 ? 'E' : 'W'}`;
    const borderHtml = (c.border_codes || []).length
      ? c.border_codes
          .map((bc) => {
            const b = this._encyAtlas.countriesByCode[bc];
            return b
              ? `<button type="button" class="ency-border-pill" data-jump-code="${escapeHtml(b.code)}"><img src="${escapeHtml(b.flag_svg)}" alt="" class="gl-tiny-flag" />${escapeHtml(b.name)}</button>`
              : '';
          })
          .join('')
      : '<span class="empty-ticker-msg">Sea-bounded / No land borders</span>';

    const traitsHtml = (c.characteristics || []).map((t) => `<li>${escapeHtml(t)}</li>`).join('');
    this.dom.encyDossier.innerHTML = `
      <div class="ency-head">
        <img src="${escapeHtml(c.flag_svg)}" alt="${escapeHtml(c.name)} flag" class="ency-hero-flag" />
        <div>
          <h3 class="ency-dossier-title">${escapeHtml(c.name)}</h3>
          <div class="ency-dossier-official">${escapeHtml(c.official_name)}</div>
          <div class="ency-dossier-loc">${escapeHtml(c.continent)} · ${escapeHtml(c.subregion)} (${latStr}, ${lngStr})</div>
        </div>
      </div>

      <div class="ency-stats-grid">
        <div class="ency-stat"><span>CAPITAL</span><strong>${escapeHtml(c.capital)}</strong></div>
        <div class="ency-stat"><span>POPULATION</span><strong>${escapeHtml(c.population_label)} (#${escapeHtml(c.population_rank)})</strong></div>
        <div class="ency-stat"><span>LAND AREA</span><strong>${escapeHtml(c.area_label)} (#${escapeHtml(c.area_rank)})</strong></div>
        <div class="ency-stat"><span>LANGUAGE &amp; CURRENCY</span><strong>${escapeHtml(c.language)} · ${escapeHtml(c.currency)}</strong></div>
      </div>

      <div class="ency-subblock">
        <h4 class="bunker-sublabel ency-dossier-sublabel">LAND BORDERS (${(c.border_codes || []).length})</h4>
        <div class="ency-border-chips">${borderHtml}</div>
      </div>

      <div class="ency-subblock">
        <h4 class="bunker-sublabel ency-dossier-sublabel">UNIQUE CHARACTERISTICS</h4>
        <ul class="ency-traits-list">${traitsHtml}</ul>
      </div>
    `;

    this.dom.encyDossier.querySelectorAll('[data-jump-code]').forEach((btn) => {
      btn.addEventListener('click', () => {
        sound.click();
        this._selectEncyclopediaCountry(btn.dataset.jumpCode);
      });
    });
  }

  _startClock() {
    const updateClock = () => {
      const now = new Date();
      this.dom.ps5Clock.textContent = now.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    };
    updateClock();
    setInterval(updateClock, 15000);
  }

  _bindEvents() {
    this.dom.entryForm.addEventListener('submit', (e) => {
      e.preventDefault();
      sound.click();
      const name = this.dom.playerNameInput.value.trim();
      if (!name) return;
      this.playerName = name;
      safeSetStorage('blackout_player_name', name);
      this._updateCallsign();
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        if (this._serverPlayerName !== name) {
          this._send({ type: 'SET_NAME', player_name: name, payload: {} });
        }
      }
      this._showView('lobby');
      if (!this.catalog.length) {
        this._renderGamesHome();
      }
    });

    document.querySelectorAll('[data-hub-tab]').forEach((btn) => {
      btn.addEventListener('click', () => {
        sound.click();
        this.selectedGameType = 'explore';
        this._renderGamesHome({ scrollRail: true });
      });
    });

    window.addEventListener('keydown', (e) => {
      const openModals = this._getOpenModals();
      if (e.key === 'Escape') {
        const closable = this._getClosableModals().filter((m) => !m.classList.contains('hidden'));
        const topClosable = closable[closable.length - 1];
        if (topClosable) {
          e.preventDefault();
          sound.click();
          this._closeModal(topClosable);
          return;
        }
      }

      if (e.key === 'Tab' && openModals.length > 0) {
        const topModal = openModals[openModals.length - 1];
        const focusables = this._getFocusableInModal(topModal);
        if (!focusables.length) {
          e.preventDefault();
          return;
        }
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (e.shiftKey) {
          if (document.activeElement === first || !topModal.contains(document.activeElement)) {
            e.preventDefault();
            last.focus();
          }
        } else if (document.activeElement === last || !topModal.contains(document.activeElement)) {
          e.preventDefault();
          first.focus();
        }
        return;
      }

      if (openModals.length > 0) return;

      const tag = document.activeElement?.tagName;
      if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return;
      if (this.currentView === 'lobby') {
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          const items = this._railItems();
          if (!items.length) return;
          e.preventDefault();
          const curIdx = Math.max(0, items.findIndex((g) => g.game_type === this.selectedGameType));
          const delta = e.key === 'ArrowRight' ? 1 : -1;
          const next = items[(curIdx + delta + items.length) % items.length];
          this.selectedGameType = next.game_type;
          sound.tick();
          this._renderGamesHome({ scrollRail: true });
          if (this.selectedGameType !== 'explore') {
            this._pulseDifficultyPrompt();
          }
        }
      }
    });

    // Settings & Personalization Triggers
    [
      this.dom.btnOpenSettings,
      this.dom.btnEntrySettings,
      this.dom.btnArenaSettings,
    ].forEach((btn) => {
      if (!btn) return;
      btn.addEventListener('click', () => {
        sound.click();
        this._openSettingsModal();
      });
    });

    this.dom.btnCloseSettings.addEventListener('click', () => {
      sound.click();
      this._closeModal(this.dom.modalSettings);
    });

    this.dom.settingsColorPicker.addEventListener('input', (e) => {
      this._applyAccentColor(e.target.value, true);
    });

    this.dom.settingsColorHex.addEventListener('input', (e) => {
      const valid = this._normalizeHex(e.target.value);
      if (valid) {
        this._applyAccentColor(valid, true);
      }
    });

    this.dom.settingsColorHex.addEventListener('blur', () => {
      this.dom.settingsColorHex.value = this.accentColor;
    });

    this.dom.btnResetAccent.addEventListener('click', () => {
      sound.click();
      this._applyAccentColor(DEFAULT_ACCENT_HEX, true);
      this._toast('Accent color reset to Subtle Red (#E5484D).');
    });

    this.dom.settingsGlassPills.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-glass]');
      if (!btn) return;
      sound.click();
      this._applyGlassIntensity(btn.dataset.glass, true);
    });

    this.dom.btnSettingsMute.addEventListener('click', () => {
      sound.toggleMute();
      this._updateMuteButtons();
      sound.click();
    });

    if (this.dom.btnArenaMute) {
      this.dom.btnArenaMute.addEventListener('click', () => {
        sound.toggleMute();
        this._updateMuteButtons();
        sound.click();
      });
    }

    this.dom.btnSettingsRename.addEventListener('click', () => {
      sound.click();
      this._closeModal(this.dom.modalSettings, { restoreFocus: false });
      this.dom.renameInput.value = this.playerName;
      this._openModal(this.dom.modalRename, this.dom.renameInput);
    });

    // Click backdrop on any overlay modal to close cleanly (except fatal gameover)
    this._getClosableModals().forEach((overlay) => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          sound.click();
          this._closeModal(overlay);
        }
      });
    });

    this._bindChessEditorEvents();

    // World Country Encyclopedia bindings
    if (this.dom.btnOpenEncyclopedia) {
      this.dom.btnOpenEncyclopedia.addEventListener('click', () => {
        sound.click();
        this._openEncyclopedia();
      });
    }
    if (this.dom.btnCloseEncyclopedia) {
      this.dom.btnCloseEncyclopedia.addEventListener('click', () => {
        sound.click();
        this._closeModal(this.dom.modalEncyclopedia);
      });
    }
    if (this.dom.encySearch) {
      this.dom.encySearch.addEventListener('input', () => this._renderEncyclopediaList());
    }
    if (this.dom.encyContinentTabs) {
      this.dom.encyContinentTabs.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-continent]');
        if (!btn) return;
        sound.click();
        this._encyContinent = btn.dataset.continent;
        this.dom.encyContinentTabs.querySelectorAll('.filter-tab').forEach((el) =>
          el.classList.toggle('active', el.dataset.continent === this._encyContinent)
        );
        this._renderEncyclopediaList();
      });
    }

    this.dom.btnCloseQuickJoin.addEventListener('click', () => {
      sound.click();
      this._closeModal(this.dom.modalQuickJoin);
    });

    const handleJoinSubmit = (inputEl) => {
      const code = inputEl.value.trim().toUpperCase();
      if (code.length < 4) {
        this._toast('Enter a valid 6-character room code.', true);
        return;
      }
      const submitBtn = this.dom.btnJoinSubmit || this.dom.modalJoinForm?.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.classList.add('is-loading');
      }
      this._closeModal(this.dom.modalQuickJoin);
      this._send({
        type: 'JOIN_ROOM',
        player_name: this.playerName,
        room_code: code,
        payload: {},
      });
    };
    this.dom.modalJoinForm.addEventListener('submit', (e) => {
      e.preventDefault();
      sound.click();
      handleJoinSubmit(this.dom.modalCodeInput);
    });

    this.dom.btnChangeName.addEventListener('click', () => {
      sound.click();
      this.dom.renameInput.value = this.playerName;
      this._openModal(this.dom.modalRename, this.dom.renameInput);
    });

    this.dom.btnCancelRename.addEventListener('click', () => {
      sound.click();
      this._closeModal(this.dom.modalRename);
    });

    this.dom.renameForm.addEventListener('submit', (e) => {
      e.preventDefault();
      sound.click();
      const name = this.dom.renameInput.value.trim();
      if (!name) return;
      this.playerName = name;
      safeSetStorage('blackout_player_name', name);
      if (this.ws && this.ws.readyState === WebSocket.OPEN && this._serverPlayerName !== name) {
        this._send({ type: 'SET_NAME', player_name: name, payload: {} });
      }
      this._updateCallsign();
      this._closeModal(this.dom.modalRename);
    });

    if (this.dom.diffPills) {
      this.dom.diffPills.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-diff]');
        if (!btn || this.selectedGameType === 'explore') return;
        sound.tick();
        this._setSelectedDifficulty(this.selectedGameType, btn.dataset.diff);
        this._renderDifficultySelector(this.selectedGameType);
      });
    }

    if (this.dom.qaCatPills) {
      this.dom.qaCatPills.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-qa-cat]');
        if (!btn) return;
        sound.tick();
        this.selectedQaCategory = btn.dataset.qaCat;
        safeSetStorage('blackout_qa_category', this.selectedQaCategory);
        this._renderDifficultySelector(this.selectedGameType);
      });
    }

    const handleMinesManualChange = (e) => {
      if (this.selectedGameType !== 'minesweeper') return;
      const wRaw = this.dom.msInputWidth?.value;
      const hRaw = this.dom.msInputHeight?.value;
      const bRaw = this.dom.msInputBooms?.value;
      const custom = this._setMinesCustomSettings(wRaw, hRaw, bRaw);
      const maxBooms = Math.min(1071, Math.max(1, custom.width * custom.height - 9));
      if (this.dom.msInputBooms) {
        this.dom.msInputBooms.max = String(maxBooms);
        if (Number(bRaw) > maxBooms || e?.type === 'change') {
          this.dom.msInputBooms.value = String(custom.booms);
        }
      }
      if (e?.type === 'change') {
        if (this.dom.msInputWidth) this.dom.msInputWidth.value = String(custom.width);
        if (this.dom.msInputHeight) this.dom.msInputHeight.value = String(custom.height);
      }
      this._setSelectedDifficulty('minesweeper', 'custom');
      this.dom.diffPills?.querySelectorAll('[data-diff]').forEach((btn) => {
        const active = btn.dataset.diff === 'custom';
        btn.classList.toggle('active', active);
        btn.setAttribute('aria-checked', String(active));
      });
      if (this.dom.difficultyHint) {
        this.dom.difficultyHint.textContent = `Custom: ${custom.width}×${custom.height} grid with ${custom.booms} booms.`;
      }
    };

    [this.dom.msInputWidth, this.dom.msInputHeight, this.dom.msInputBooms].forEach((input) => {
      if (!input) return;
      input.addEventListener('input', handleMinesManualChange);
      input.addEventListener('change', handleMinesManualChange);
    });

    const handleBunkerMinesChange = (e) => {
      if (this.activeGameType !== 'minesweeper') return;
      const wRaw = this.dom.bunkerMsWidth?.value;
      const hRaw = this.dom.bunkerMsHeight?.value;
      const bRaw = this.dom.bunkerMsBooms?.value;
      const custom = this._setMinesCustomSettings(wRaw, hRaw, bRaw);
      const maxBooms = Math.min(1071, Math.max(1, custom.width * custom.height - 9));
      if (this.dom.bunkerMsBooms) {
        this.dom.bunkerMsBooms.max = String(maxBooms);
        if (Number(bRaw) > maxBooms || e?.type === 'change') {
          this.dom.bunkerMsBooms.value = String(custom.booms);
        }
      }
      if (e?.type === 'change') {
        if (this.dom.bunkerMsWidth) this.dom.bunkerMsWidth.value = String(custom.width);
        if (this.dom.bunkerMsHeight) this.dom.bunkerMsHeight.value = String(custom.height);
      }
      clearTimeout(this._bunkerMinesTimer);
      const emit = () => {
        this.sendGameAction('update_settings', {
          difficulty: 'custom',
          width: custom.width,
          height: custom.height,
          rows: custom.height,
          cols: custom.width,
          mines: custom.booms,
          booms: custom.booms,
        });
      };
      if (e?.type === 'change') {
        sound.click();
        emit();
      } else {
        this._bunkerMinesTimer = setTimeout(emit, 260);
      }
    };

    [this.dom.bunkerMsWidth, this.dom.bunkerMsHeight, this.dom.bunkerMsBooms].forEach((input) => {
      if (!input) return;
      input.addEventListener('input', handleBunkerMinesChange);
      input.addEventListener('change', handleBunkerMinesChange);
    });

    if (this.dom.btnToggleComms) {
      this.dom.btnToggleComms.addEventListener('click', () => {
        sound.click();
        this._toggleComms();
      });
    }
    if (this.dom.btnCloseComms) {
      this.dom.btnCloseComms.addEventListener('click', () => {
        sound.click();
        this._toggleComms(false);
      });
    }
    if (this.dom.arenaChatForm) {
      this.dom.arenaChatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = (this.dom.arenaChatInput?.value || '').trim().slice(0, 280);
        if (!text || !this.currentRoom) return;
        sound.tick();
        this._send({
          type: 'CHAT_MSG',
          player_name: this.playerName,
          room_code: this.currentRoom,
          game_type: this.activeGameType,
          payload: { action: 'chat', data: { text } },
        });
        this.dom.arenaChatInput.value = '';
      });
    }

    // Pre-Game Setup Matchup & Stepper Events
    if (this.dom.btnMatchupAi) {
      this.dom.btnMatchupAi.addEventListener('click', () => {
        if (this.dom.btnMatchupAi.disabled) return;
        sound.click();
        this.pregameSetup.matchupType = 'ai';
        this._syncPregameSetup(this.selectedGameType);
      });
    }

    if (this.dom.btnMatchupHost) {
      this.dom.btnMatchupHost.addEventListener('click', () => {
        if (this.dom.btnMatchupHost.disabled) return;
        sound.click();
        this.pregameSetup.matchupType = 'host';
        this._syncPregameSetup(this.selectedGameType);
      });
    }

    if (this.dom.btnPlayerCountDec) {
      this.dom.btnPlayerCountDec.addEventListener('click', () => {
        if (this.dom.btnPlayerCountDec.disabled) return;
        if (this.pregameSetup.playerCount > this.pregameSetup.minPlayers) {
          sound.tick();
          this.pregameSetup.playerCount--;
          this._syncPregameSetup(this.selectedGameType);
        }
      });
    }

    if (this.dom.btnPlayerCountInc) {
      this.dom.btnPlayerCountInc.addEventListener('click', () => {
        if (this.dom.btnPlayerCountInc.disabled) return;
        if (this.pregameSetup.playerCount < this.pregameSetup.maxPlayers) {
          sound.tick();
          this.pregameSetup.playerCount++;
          this._syncPregameSetup(this.selectedGameType);
        }
      });
    }

    if (this.dom.btnPregameLaunch) {
      this.dom.btnPregameLaunch.addEventListener('click', () => {
        this._launchPregameSession();
      });
    }

    if (this.dom.btnHeroSolo) {
      this.dom.btnHeroSolo.addEventListener('click', () => {
        this.pregameSetup.matchupType = 'ai';
        this._launchPregameSession();
      });
    }

    if (this.dom.btnHeroHost) {
      this.dom.btnHeroHost.addEventListener('click', () => {
        this.pregameSetup.matchupType = 'host';
        this._launchPregameSession();
      });
    }

    if (this.dom.btnHeroJoin) {
      this.dom.btnHeroJoin.addEventListener('click', () => {
        sound.click();
        const filterGame = this.selectedGameType === 'explore' ? null : this.selectedGameType;
        this._openJoinModal(filterGame);
      });
    }

    const copyCodeFn = async () => {
      sound.click();
      const code = this.currentRoom;
      if (!code) return;
      try {
        await navigator.clipboard.writeText(code);
        this._toast(`Room code ${code} copied to clipboard.`);
      } catch {
        this._toast(`Room code: ${code}`);
      }
    };
    this.dom.btnCopyCode.addEventListener('click', copyCodeFn);

    const leaveFn = () => {
      sound.click();
      this._leaveRoomToLobby();
    };
    this.dom.btnLeaveRoom.addEventListener('click', leaveFn);

    const togglePinHelp = () => {
      sound.click();
      this.helpPinned = !this.helpPinned;
      this._renderPinnedHelp();
    };
    this.dom.btnPinHelp.addEventListener('click', togglePinHelp);
    this.dom.btnUnpinHelp.addEventListener('click', () => {
      sound.click();
      this.helpPinned = false;
      this._renderPinnedHelp();
    });

    this.dom.btnAddBot.addEventListener('click', () => {
      sound.click();
      this.sendGameAction('add_bot', {});
    });

    this.dom.btnRemoveBot.addEventListener('click', () => {
      sound.click();
      this.sendGameAction('remove_bot', {});
    });

    this.dom.btnStartMatch.addEventListener('click', () => {
      sound.click();
      this.dom.btnStartMatch.disabled = true;
      this.dom.btnStartMatch.classList.add('is-loading');
      this._send({
        type: 'START_GAME',
        player_name: this.playerName,
        room_code: this.currentRoom,
        game_type: this.activeGameType,
        payload: { action: 'start', data: {} },
      });
    });

    this.dom.btnRematch.addEventListener('click', () => {
      sound.click();
      this._closeModal(this.dom.modalGameover, { restoreFocus: false });
      this.sendGameAction('rematch', {});
    });

    this.dom.btnGameoverLobby.addEventListener('click', () => {
      sound.click();
      this._closeModal(this.dom.modalGameover, { restoreFocus: false });
      this._leaveRoomToLobby();
    });

    this.dom.btnOpenLeaderboard.addEventListener('click', async () => {
      sound.click();
      try {
        const res = await fetch('/api/leaderboard');
        const json = await res.json();
        this.leaderboard = json.leaderboard || {};
      } catch {
        // Fallback to cached lobby leaderboard
      }
      this._renderLeaderboardModal();
      this._openModal(this.dom.modalLeaderboard, this.dom.btnCloseLeaderboard);
    });

    this.dom.btnCloseLeaderboard.addEventListener('click', () => {
      sound.click();
      this._closeModal(this.dom.modalLeaderboard);
    });
  }

  _launchActivity(gameType, data) {
    this.lastPlayedGame = gameType;
    this.selectedGameType = gameType;
    safeSetStorage('blackout_last_game', gameType);
    this._send({
      type: 'CREATE_ROOM',
      player_name: this.playerName,
      game_type: gameType,
      payload: { action: 'create', data },
    });
  }

  _setWsStatus(isOnline) {
    if (this.dom.wsStatusDot) {
      this.dom.wsStatusDot.classList.toggle('is-online', isOnline);
      this.dom.wsStatusDot.classList.toggle('is-offline', !isOnline);
    }
    if (this.dom.wsStatusEntry) {
      this.dom.wsStatusEntry.textContent = isOnline ? 'BROADCAST LINK ONLINE' : 'RECONNECTING...';
    }
    if (this.dom.topbarWsStatus) {
      this.dom.topbarWsStatus.classList.toggle('is-online', isOnline);
      this.dom.topbarWsStatus.classList.toggle('is-offline', !isOnline);
      this.dom.topbarWsStatus.title = isOnline ? 'Network Link: Online' : 'Network Link: Reconnecting...';
      this.dom.topbarWsStatus.setAttribute('aria-label', isOnline ? 'Network Link: Online' : 'Network Link: Reconnecting...');
    }
    if (this.dom.hudWsStatus) {
      this.dom.hudWsStatus.classList.toggle('is-online', isOnline);
      this.dom.hudWsStatus.classList.toggle('is-offline', !isOnline);
      this.dom.hudWsStatus.title = isOnline ? 'Network Link: Online' : 'Network Link: Reconnecting...';
      this.dom.hudWsStatus.setAttribute('aria-label', isOnline ? 'Network Link: Online' : 'Network Link: Reconnecting...');
    }
  }

  _connectWS() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const secretParam = this.sessionSecret ? `?secret=${encodeURIComponent(this.sessionSecret)}` : '';
    const url = `${proto}//${window.location.host}/ws/${encodeURIComponent(this.clientId)}${secretParam}`;
    this.ws = new WebSocket(url);

    this.ws.addEventListener('open', () => {
      this._serverPlayerName = '';
      this._sentNameOnConn = false;
      this._setWsStatus(true);
      this._resetActionLoadingStates();
      if (this.playerName) {
        if (!this.currentRoom) {
          this._send({ type: 'SET_NAME', player_name: this.playerName, payload: {} });
          this._sentNameOnConn = true;
          this._showView('lobby');
          this._updateCallsign();
        }
      }
    });

    this.ws.addEventListener('message', (event) => {
      let msg;
      try {
        msg = JSON.parse(event.data);
      } catch {
        return;
      }
      this._handleServerMessage(msg);
    });

    this.ws.addEventListener('close', (event) => {
      this._serverPlayerName = '';
      this._setWsStatus(false);
      this._resetActionLoadingStates();
      if (event?.code === 4003) {
        this.sessionSecret = '';
        safeSetStorage('blackout_session_secret', '', 'session');
      }
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = setTimeout(() => this._connectWS(), 1500);
    });
  }

  _send(envelope) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this._resetActionLoadingStates();
      this._toast('Connection lost. Reconnecting...', true);
      return;
    }
    this.ws.send(JSON.stringify(envelope));
  }

  sendGameAction(action, data = {}) {
    this._send({
      type: 'GAME_ACTION',
      player_name: this.playerName,
      room_code: this.currentRoom,
      game_type: this.activeGameType,
      payload: { action, data },
    });
  }

  _clearRoomState() {
    this._destroyActiveGame();
    clearTimeout(this._bunkerMinesTimer);
    this.currentRoom = null;
    this.activeGameType = null;
    this.publicState = null;
    this.privateState = {};
    this.players = [];
    this.helpPinned = false;
    this._bunkerSchemaKey = '';
    this._resetComms();
    this._resetActionLoadingStates();
    this._closeModal(this.dom.modalGameover, { restoreFocus: false });
  }

  _handleServerMessage(msg) {
    const { type, room_code, game_type, public_state, private_state, players, message } = msg;

    if (type === 'ERROR') {
      sound.error();
      this._resetActionLoadingStates();
      this._toast(message || 'Action rejected.', true);
      return;
    }

    if (type === 'LOBBY_STATE') {
      this.catalog = public_state?.games || [];
      this.openRooms = public_state?.open_rooms || [];
      this.leaderboard = public_state?.leaderboard || {};
      if (private_state?.session_secret) {
        this.sessionSecret = private_state.session_secret;
        safeSetStorage('blackout_session_secret', this.sessionSecret, 'session');
      }
      this._serverPlayerName = private_state?.player_name || '';

      if (this.currentRoom) {
        this._clearRoomState();
        this._showView(this.playerName ? 'lobby' : 'entry');
      }

      if (
        this.playerName &&
        !this._serverPlayerName &&
        !this._sentNameOnConn &&
        this.ws?.readyState === WebSocket.OPEN
      ) {
        this._sentNameOnConn = true;
        this._send({ type: 'SET_NAME', player_name: this.playerName, payload: {} });
      }

      this._renderGamesHome();
      if (!this.dom.modalQuickJoin.classList.contains('hidden')) {
        this._renderJoinModalRooms();
      }
      return;
    }

    // Defense-in-depth room isolation: ignore broadcasts for empty/abandoned or mismatched rooms
    if (
      (type === 'ROOM_UPDATE' ||
        type === 'GAME_STATE' ||
        type === 'PRIVATE_STATE' ||
        type === 'GAME_OVER') &&
      (!this.currentRoom || (room_code && room_code !== this.currentRoom))
    ) {
      return;
    }

    if (type === 'ROOM_JOINED' || type === 'ROOM_UPDATE') {
      const prevRoom = this.currentRoom;
      this.currentRoom = room_code || this.currentRoom;
      this.activeGameType = game_type;
      this.publicState = public_state || {};
      if (type === 'ROOM_JOINED') {
        this._resetActionLoadingStates();
        if (prevRoom !== room_code) {
          this._resetComms();
        }
        this.privateState =
          private_state && Object.keys(private_state).length > 0 ? private_state : {};
      } else if (private_state && Object.keys(private_state).length > 0) {
        this.privateState = private_state;
      } else if (this.publicState?.room_meta?.phase === 'waiting') {
        this.privateState = {};
      }
      this.players = players || [];
      this._showView('arena');
      this._renderArenaChrome();
      if (this.publicState?.room_meta?.phase !== 'waiting') {
        this._syncGameModule();
      }
      return;
    }

    if (type === 'GAME_STARTED') {
      this._resetActionLoadingStates();
      this._closeModal(this.dom.modalGameover, { restoreFocus: false });
      this.currentRoom = room_code;
      this.activeGameType = game_type;
      this.publicState = public_state || {};
      this.privateState = {};
      this.players = players || [];
      this._showView('arena');
      this._renderArenaChrome();
      this._mountGameModule(game_type);
      return;
    }

    if (type === 'GAME_STATE') {
      this.publicState = public_state || {};
      this.players = players || [];
      this._renderArenaChrome();
      this._syncGameModule();
      return;
    }

    if (type === 'PRIVATE_STATE') {
      this.privateState = private_state || {};
      this._syncGameModule();
      return;
    }

    if (type === 'GAME_OVER') {
      this.publicState = public_state || {};
      this.players = players || [];
      this._renderArenaChrome();
      this._syncGameModule();
      this._showGameOverModal(message);
    }
  }

  _showView(name) {
    this.currentView = name;
    document.body.classList.toggle('in-console', name !== 'entry');
    this.dom.viewEntry.classList.toggle('hidden', name !== 'entry');
    this.dom.viewLobby.classList.toggle('hidden', name !== 'lobby');
    this.dom.viewArena.classList.toggle('hidden', name !== 'arena');
    this._renderPinnedHelp();
  }

  _updateCallsign() {
    const upper = this.playerName.toUpperCase();
    this.dom.lobbyCallsign.textContent = `CALLSIGN: ${upper}`;
    this.dom.avatarInitial.textContent = upper ? upper[0] : 'A';
  }

  _updateMuteButtons() {
    const muted = sound.isMuted();
    const label = muted ? 'SFX: OFF' : 'SFX: ON';
    if (this.dom.btnSettingsMute) {
      this.dom.btnSettingsMute.textContent = label;
      this.dom.btnSettingsMute.setAttribute('aria-pressed', String(muted));
    }
    if (this.dom.btnArenaMute) {
      this.dom.btnArenaMute.textContent = label;
      this.dom.btnArenaMute.setAttribute('aria-pressed', String(muted));
    }
  }

  _normalizeDifficulty(raw) {
    const k = String(raw || '').trim().toLowerCase();
    if (k === 'easy' || k === 'beginner') return 'easy';
    if (k === 'hard' || k === 'expert') return 'hard';
    if (k === 'custom' || k === 'custem' || k === 'manual') return 'custom';
    return 'mid';
  }

  _getMinesCustomSettings() {
    try {
      const parsed = JSON.parse(safeGetStorage('blackout_mines_custom', '{}') || '{}');
      if (parsed && typeof parsed === 'object') {
        const width = Math.max(8, Math.min(36, Number(parsed.width) || 16));
        const height = Math.max(8, Math.min(30, Number(parsed.height) || 16));
        const maxBooms = Math.min(1071, Math.max(1, (width * height) - 9));
        const booms = Math.max(1, Math.min(maxBooms, Number(parsed.booms) || 40));
        return { width, height, booms };
      }
    } catch {}
    return { width: 16, height: 16, booms: 40 };
  }

  _setMinesCustomSettings(w, h, b) {
    const width = Math.max(8, Math.min(36, Number(w) || 16));
    const height = Math.max(8, Math.min(30, Number(h) || 16));
    const maxBooms = Math.min(1071, Math.max(1, (width * height) - 9));
    const booms = Math.max(1, Math.min(maxBooms, Number(b) || 40));
    safeSetStorage('blackout_mines_custom', JSON.stringify({ width, height, booms }));
    return { width, height, booms };
  }

  _loadDifficultyMap() {
    try {
      const parsed = JSON.parse(safeGetStorage('blackout_difficulty_map', '{}') || '{}');
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch {
      return {};
    }
  }

  _getSelectedDifficulty(gameType) {
    return this._normalizeDifficulty(this.selectedDifficultyByGame?.[gameType] || 'mid');
  }

  _setSelectedDifficulty(gameType, diff) {
    if (!gameType || gameType === 'explore') return;
    this.selectedDifficultyByGame[gameType] = this._normalizeDifficulty(diff);
    safeSetStorage('blackout_difficulty_map', JSON.stringify(this.selectedDifficultyByGame));
  }

  _pulseDifficultyPrompt() {
    if (!this.dom.difficultyWrap) return;
    this.dom.difficultyWrap.classList.add('is-prompting');
    clearTimeout(this._diffPulseTimer);
    this._diffPulseTimer = setTimeout(() => {
      this.dom.difficultyWrap?.classList.remove('is-prompting');
    }, 650);
  }

  _heroLaunchSettings(gameType) {
    const diff = this._getSelectedDifficulty(gameType);
    const settings = { difficulty: diff };
    if (gameType === 'qa_trivia') {
      settings.category = this.selectedQaCategory || 'All';
    } else if (gameType === 'minesweeper' && diff === 'custom') {
      const custom = this._getMinesCustomSettings();
      settings.width = custom.width;
      settings.height = custom.height;
      settings.rows = custom.height;
      settings.cols = custom.width;
      settings.mines = custom.booms;
      settings.booms = custom.booms;
    }
    return settings;
  }

  _renderDifficultySelector(gameType) {
    if (!this.dom.difficultyWrap) return;
    const isExplore = !gameType || gameType === 'explore';
    this.dom.difficultyWrap.classList.toggle('hidden', isExplore);
    if (isExplore) return;
    const diff = this._getSelectedDifficulty(gameType);
    this.dom.diffPills?.querySelectorAll('[data-diff]').forEach((btn) => {
      const active = btn.dataset.diff === diff;
      btn.classList.toggle('active', active);
      btn.setAttribute('aria-checked', String(active));
    });
    const isQa = gameType === 'qa_trivia';
    if (this.dom.qaCategoryRow) {
      this.dom.qaCategoryRow.classList.toggle('hidden', !isQa);
    }
    if (isQa && this.dom.qaCatPills) {
      this.dom.qaCatPills.querySelectorAll('[data-qa-cat]').forEach((btn) => {
        const active = btn.dataset.qaCat === this.selectedQaCategory;
        btn.classList.toggle('active', active);
        btn.setAttribute('aria-checked', String(active));
      });
    }

    const isMines = gameType === 'minesweeper';
    if (this.dom.diffBtnCustom) {
      this.dom.diffBtnCustom.classList.toggle('hidden', !isMines);
    }
    if (this.dom.minesCustomRow) {
      this.dom.minesCustomRow.classList.toggle('hidden', !isMines);
    }
    if (isMines) {
      let w = 16, h = 16, b = 40;
      if (diff === 'easy') { w = 9; h = 9; b = 10; }
      else if (diff === 'mid') { w = 16; h = 16; b = 40; }
      else if (diff === 'hard') { w = 30; h = 16; b = 99; }
      else if (diff === 'custom') {
        const custom = this._getMinesCustomSettings();
        w = custom.width; h = custom.height; b = custom.booms;
      }
      const maxBooms = Math.min(1071, Math.max(1, w * h - 9));
      if (this.dom.msInputWidth) this.dom.msInputWidth.value = w;
      if (this.dom.msInputHeight) this.dom.msInputHeight.value = h;
      if (this.dom.msInputBooms) {
        this.dom.msInputBooms.max = String(maxBooms);
        this.dom.msInputBooms.value = Math.min(maxBooms, b);
      }
      if (diff === 'custom') {
        this.dom.difficultyHint.textContent = `Custom: ${w}×${h} grid with ${b} booms.`;
        return;
      }
    }

    const notes = GAME_HUB_META[gameType]?.difficultyNotes || {};
    this.dom.difficultyHint.textContent =
      notes[diff] || `Difficulty set to ${diff.toUpperCase()}.`;
  }

  _openJoinModal(filterGameType = null) {
    this.joinModalFilterGame = filterGameType || null;
    this._renderJoinModalRooms();
    this._openModal(this.dom.modalQuickJoin, this.dom.modalCodeInput);
  }

  _renderJoinModalRooms() {
    if (!this.dom.modalOpenRooms) return;
    const filterType = this.joinModalFilterGame;
    const activeMeta = filterType ? this.catalog.find((g) => g.game_type === filterType) : null;
    this.dom.modalJoinTitle.textContent = activeMeta
      ? `Join ${activeMeta.title}`
      : 'Join Room';
    this.dom.modalJoinRoomsLabel.textContent = activeMeta
      ? `Open ${activeMeta.title} Rooms`
      : 'Live Public Rooms';

    const rooms = filterType
      ? this.openRooms.filter((r) => r.game_type === filterType)
      : this.openRooms;

    this.dom.modalOpenRooms.innerHTML = '';
    if (!rooms.length) {
      const msg = document.createElement('p');
      msg.className = 'empty-ticker-msg';
      msg.textContent = activeMeta
        ? `No open ${activeMeta.title} rooms broadcasting right now. Enter a private room code below or choose Host Game.`
        : 'No open rooms broadcasting right now. Enter a private room code below or Host Game.';
      this.dom.modalOpenRooms.appendChild(msg);
    } else {
      for (const room of rooms) {
        this.dom.modalOpenRooms.appendChild(this._buildRoomRow(room));
      }
    }
  }

  _railItems() {
    const exploreEntry = {
      game_type: 'explore',
      title: 'Blackout Arcade',
      description: 'Eleven classic strategy, world geography, tabletop, card, QA trivia & arcade games running on one real-time liquid glass console.',
      supports_solo: true,
    };
    return [exploreEntry, ...this.catalog];
  }

  _renderGamesHome({ scrollRail = false } = {}) {
    const list = this._railItems();
    const listSignature = list.map((g) => g.game_type).join(',');

    if (this._railSignature !== listSignature) {
      this._railSignature = listSignature;
      this.dom.ps5GameRail.innerHTML = '';

      for (const g of list) {
        const meta = GAME_HUB_META[g.game_type] || {};
        const tile = document.createElement('button');
        tile.type = 'button';
        tile.dataset.gameType = g.game_type;
        tile.className = 'ps5-rail-tile';
        tile.setAttribute('role', 'option');

        const icon = document.createElement('span');
        icon.className = 'ps5-rail-icon';
        icon.innerHTML = GAME_HAZARD_ICONS[g.game_type] || '';

        const label = document.createElement('span');
        label.className = 'ps5-rail-label';
        label.textContent = meta.shortTitle || g.title;

        tile.append(icon, label);
        tile.addEventListener('click', () => {
          const changed = this.selectedGameType !== g.game_type;
          this.selectedGameType = g.game_type;
          sound.tick();
          if (changed) {
            this.pregameSetup.selectedModeIndex = 0;
            this._renderGamesHome({ scrollRail: true });
          }
          if (g.game_type !== 'explore') {
            this._pulseDifficultyPrompt();
          }
        });
        this.dom.ps5GameRail.appendChild(tile);
      }
    }

    this.dom.ps5GameRail.querySelectorAll('.ps5-rail-tile').forEach((tile) => {
      const isSelected = tile.dataset.gameType === this.selectedGameType;
      tile.classList.toggle('active', isSelected);
      tile.setAttribute('aria-selected', String(isSelected));
      if (isSelected && scrollRail) {
        tile.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    });

    const active = list.find((g) => g.game_type === this.selectedGameType) || list[0];
    if (!active) return;

    const isExplore = active.game_type === 'explore';
    const hub = GAME_HUB_META[active.game_type] || {};
    this.dom.ps5HeroArt.innerHTML = renderGameHeroArt(active.game_type);
    this.dom.ps5HeroMeta.textContent = isExplore
      ? `Official Broadcast Hub | ${this.openRooms.length} Open Rooms`
      : `${hub.badge || active.category} | ${hub.estTime || '5 MIN'}`;
    this.dom.ps5HeroTitle.textContent = active.title;
    this.dom.ps5HeroDesc.textContent = active.description;
    this._renderDifficultySelector(active.game_type);

    if (isExplore) {
      const resumeTitle = GAME_HUB_META[this.lastPlayedGame]?.shortTitle || 'Chess';
      this.dom.btnHeroSolo.textContent = `Quick Play: ${resumeTitle}`;
      this.dom.btnHeroHost.classList.add('hidden');
      if (this.dom.btnHeroJoin) this.dom.btnHeroJoin.textContent = 'Join Room';
    } else {
      this.dom.btnHeroSolo.textContent = active.supports_solo ? 'Play Solo' : 'Play Solo (vs AI)';
      this.dom.btnHeroHost.classList.remove('hidden');
      this.dom.btnHeroHost.textContent = 'Host Game';
      if (this.dom.btnHeroJoin) this.dom.btnHeroJoin.textContent = 'Join Game';
    }

    // Bottom 16:9 Visual Cards Strip
    this.dom.ps5ActivityStrip.innerHTML = '';
    const activities = hub.activities || [];
    const stripWrap = document.querySelector('.ps5-bottom-strip-wrap');
    if (!activities.length) {
      if (stripWrap) stripWrap.classList.add('hidden');
    } else {
      if (stripWrap) stripWrap.classList.remove('hidden');
      activities.forEach((act, idx) => {
        const gt = act.gameType || active.game_type;
        const thumbIdx = act.thumbIdx ?? idx;
        this.dom.ps5ActivityStrip.appendChild(this._createVisualCard(gt, act, thumbIdx, idx));
      });
    }

    // Sync pre-game setup state and UI
    this._syncPregameSetup(active.game_type);

    // Below-the-Fold Details: Contextual Game Help
    this.dom.ps5ControlsLine.textContent = `CONTROLS: ${hub.controls || 'Mouse / Keyboard'}`;
    this.dom.ps5HelpCards.innerHTML = '';
    for (const tip of hub.helpTips || []) {
      const card = document.createElement('div');
      card.className = 'help-card';
      const titleEl = document.createElement('div');
      titleEl.className = 'help-card-title';
      titleEl.textContent = tip.title;
      const bodyEl = document.createElement('div');
      bodyEl.className = 'help-card-body';
      bodyEl.textContent = tip.body;
      card.append(titleEl, bodyEl);
      this.dom.ps5HelpCards.appendChild(card);
    }

    // Live Open Rooms (all if Explore, else filtered to selected module)
    const matchingRooms = isExplore
      ? this.openRooms
      : this.openRooms.filter((r) => r.game_type === active.game_type);
    this.dom.ps5GameRooms.innerHTML = '';
    if (!matchingRooms.length) {
      this.dom.ps5GameRooms.innerHTML = '<p class="empty-ticker-msg">No open rooms broadcasting right now.</p>';
    } else {
      for (const room of matchingRooms) {
        this.dom.ps5GameRooms.appendChild(this._buildRoomRow(room));
      }
    }

    // Top Bunker Records
    const recTarget = isExplore ? this.lastPlayedGame : active.game_type;
    const rows = (this.leaderboard[recTarget] || []).slice(0, 5);
    this.dom.ps5GameRecords.innerHTML = '';
    if (!rows.length) {
      this.dom.ps5GameRecords.innerHTML = '<p class="empty-ticker-msg">No victories recorded yet for this module.</p>';
    } else {
      const tbl = document.createElement('table');
      tbl.className = 'leaderboard-table';
      tbl.innerHTML = '<thead><tr><th>RANK</th><th>CALLSIGN</th><th>WINS</th><th>BEST</th></tr></thead><tbody></tbody>';
      const tbody = tbl.querySelector('tbody');
      rows.forEach((r, idx) => {
        const tr = document.createElement('tr');
        [`#${idx + 1}`, r.name, r.wins, r.best_score].forEach((val) => {
          const td = document.createElement('td');
          td.textContent = String(val);
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
      this.dom.ps5GameRecords.appendChild(tbl);
    }
  }

  _createVisualCard(gameType, act, idx = 0, modeIdx = 0) {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'visual-activity-card';
    card.setAttribute('role', 'tab');
    card.setAttribute('data-mode-idx', String(modeIdx));
    card.setAttribute('data-game-type', gameType);

    const isActive = this.selectedGameType !== 'explore' && modeIdx === this.pregameSetup.selectedModeIndex;
    if (isActive) {
      card.classList.add('active');
      card.setAttribute('aria-selected', 'true');
    } else {
      card.setAttribute('aria-selected', 'false');
    }

    card.innerHTML = `
      <div class="visual-card-art">${renderActivityThumb(gameType, idx)}</div>
      <span class="visual-card-active-pill" aria-hidden="true">ACTIVE</span>
      <div class="visual-card-overlay">
        <span class="visual-card-est">${escapeHtml(act.est)}</span>
        <span class="visual-card-title"></span>
      </div>
    `;
    card.querySelector('.visual-card-title').textContent = act.title;
    card.addEventListener('click', () => {
      sound.click();
      if (this.selectedGameType === 'explore') {
        const targetGt = act.gameType || gameType;
        this.selectedGameType = targetGt;
        this.pregameSetup.selectedModeIndex = 0;
        this._renderGamesHome({ scrollRail: true });
        return;
      }

      // Single active card invariant: deactivate all mode cards in strip
      const allCards = this.dom.ps5ActivityStrip.querySelectorAll('.visual-activity-card');
      allCards.forEach((c) => {
        c.classList.remove('active');
        c.setAttribute('aria-selected', 'false');
      });

      card.classList.add('active');
      card.setAttribute('aria-selected', 'true');
      this.pregameSetup.selectedModeIndex = modeIdx;

      // Sync pre-game setup state and UI
      this._syncPregameSetup(gameType);
    });
    return card;
  }

  _syncPregameSetup(gameType) {
    if (!this.dom.pregameSetupPanel) return;
    const isExplore = gameType === 'explore';
    const hub = GAME_HUB_META[gameType] || {};
    const activities = hub.activities || [];
    const activeCat = this.catalog.find((g) => g.game_type === gameType);

    if (isExplore) {
      if (this.dom.pregameMatchupRow) this.dom.pregameMatchupRow.classList.add('hidden');
      if (this.dom.pregamePlayerCountRow) this.dom.pregamePlayerCountRow.classList.add('hidden');
      if (this.dom.btnPregameLaunch) this.dom.btnPregameLaunch.textContent = 'Explore Modes Below';
      return;
    }

    if (this.dom.pregameMatchupRow) this.dom.pregameMatchupRow.classList.remove('hidden');
    if (this.dom.pregamePlayerCountRow) this.dom.pregamePlayerCountRow.classList.remove('hidden');

    const modeIdx = Math.max(0, Math.min(activities.length - 1, this.pregameSetup.selectedModeIndex || 0));
    this.pregameSetup.selectedModeIndex = modeIdx;
    const mode = activities[modeIdx];

    // Determine min and max player limits for current mode / game
    const minP = typeof mode?.minPlayers === 'number'
      ? mode.minPlayers
      : (activeCat?.min_players ?? 1);
    const maxP = typeof mode?.maxPlayers === 'number'
      ? mode.maxPlayers
      : (activeCat?.max_players ?? 1);

    this.pregameSetup.minPlayers = minP;
    this.pregameSetup.maxPlayers = maxP;

    // Enforce dynamic clamping of player count
    let count = typeof this.pregameSetup.playerCount === 'number' ? this.pregameSetup.playerCount : minP;
    if (count < minP) count = minP;
    if (count > maxP) count = maxP;
    this.pregameSetup.playerCount = count;

    // Determine matchup availability
    const supportsSolo = mode
      ? Boolean(mode.supportsSolo ?? mode.solo)
      : Boolean(activeCat?.supports_solo || activeCat?.supports_bots);
    const supportsHost = mode
      ? Boolean(mode.supportsHost ?? !mode.solo)
      : true;

    if (!supportsSolo && this.pregameSetup.matchupType === 'ai') {
      this.pregameSetup.matchupType = 'host';
    } else if (!supportsHost && this.pregameSetup.matchupType === 'host') {
      this.pregameSetup.matchupType = 'ai';
    }

    // Update Matchup UI
    if (this.dom.btnMatchupAi) {
      const isAi = this.pregameSetup.matchupType === 'ai';
      this.dom.btnMatchupAi.classList.toggle('active', isAi);
      this.dom.btnMatchupAi.setAttribute('aria-checked', String(isAi));
      this.dom.btnMatchupAi.disabled = !supportsSolo;
      this.dom.btnMatchupAi.classList.toggle('disabled', !supportsSolo);
      const isPureSolo = activeCat && activeCat.supports_solo && !activeCat.supports_bots;
      this.dom.btnMatchupAi.textContent = isPureSolo ? 'Solo Challenge' : 'Challenge AI';
    }

    if (this.dom.btnMatchupHost) {
      const isHost = this.pregameSetup.matchupType === 'host';
      this.dom.btnMatchupHost.classList.toggle('active', isHost);
      this.dom.btnMatchupHost.setAttribute('aria-checked', String(isHost));
      this.dom.btnMatchupHost.disabled = !supportsHost;
      this.dom.btnMatchupHost.classList.toggle('disabled', !supportsHost);
      this.dom.btnMatchupHost.textContent = 'Host vs Player';
    }

    // Update Player Range Badge
    if (this.dom.pregamePlayerRangeBadge) {
      if (minP === maxP) {
        this.dom.pregamePlayerRangeBadge.textContent = `${minP} ${minP === 1 ? 'PLAYER' : 'PLAYERS'} (LOCKED)`;
      } else {
        this.dom.pregamePlayerRangeBadge.textContent = `${minP}–${maxP} PLAYERS`;
      }
    }

    // Update Stepper Value & Button Disabled States
    if (this.dom.pregamePlayerCountVal) {
      this.dom.pregamePlayerCountVal.textContent = String(count);
    }
    if (this.dom.btnPlayerCountDec) {
      const canDec = count > minP;
      this.dom.btnPlayerCountDec.disabled = !canDec;
      this.dom.btnPlayerCountDec.classList.toggle('disabled', !canDec);
    }
    if (this.dom.btnPlayerCountInc) {
      const canInc = count < maxP;
      this.dom.btnPlayerCountInc.disabled = !canInc;
      this.dom.btnPlayerCountInc.classList.toggle('disabled', !canInc);
    }

    // Update Launch CTA text
    if (this.dom.btnPregameLaunch) {
      if (this.pregameSetup.matchupType === 'ai') {
        if (activeCat?.supports_bots) {
          const bots = Math.max(1, count - 1);
          this.dom.btnPregameLaunch.textContent = `Start AI Match (1 vs ${bots} Bot${bots > 1 ? 's' : ''})`;
        } else {
          this.dom.btnPregameLaunch.textContent = 'Start Solo Challenge';
        }
      } else {
        this.dom.btnPregameLaunch.textContent = `Host Game (${count} Players)`;
      }
    }
  }

  _launchPregameSession() {
    sound.click();
    const targetType = this.selectedGameType === 'explore' ? this.lastPlayedGame : this.selectedGameType;
    if (!targetType) return;
    const hub = GAME_HUB_META[targetType] || {};
    const activities = hub.activities || [];
    const modeIdx = Math.max(0, Math.min(activities.length - 1, this.pregameSetup.selectedModeIndex || 0));
    const mode = activities[modeIdx] || {};

    if (mode.action === 'custom_chess') {
      this._openChessCustomEditor();
      return;
    }

    const minP = this.pregameSetup.minPlayers;
    const maxP = this.pregameSetup.maxPlayers;
    const count = this.pregameSetup.playerCount;

    // Enforce bounds strictly: values below min or above max cannot be submitted
    if (count < minP || count > maxP) {
      this._toast(`Player count must be between ${minP} and ${maxP}.`);
      return;
    }

    if (this.dom.btnPregameLaunch) {
      this.dom.btnPregameLaunch.disabled = true;
      this.dom.btnPregameLaunch.classList.add('is-loading');
    }

    const activeCat = this.catalog.find((g) => g.game_type === targetType);
    const isAi = this.pregameSetup.matchupType === 'ai';
    const supportsBots = Boolean(activeCat?.supports_bots);

    const payloadData = {
      solo: isAi,
      is_public: !isAi,
      player_count: count,
      bot_count: isAi ? (supportsBots ? Math.max(0, count - 1) : 0) : 0,
      settings: {
        difficulty: this._getSelectedDifficulty(targetType),
        ...(mode.settings || {}),
      },
    };

    this._launchActivity(targetType, payloadData);
  }

  _resetActionLoadingStates() {
    if (this.dom.btnPregameLaunch) {
      this.dom.btnPregameLaunch.disabled = false;
      this.dom.btnPregameLaunch.classList.remove('is-loading');
      this._syncPregameSetup();
    }
    if (this.dom.btnStartMatch) {
      this.dom.btnStartMatch.classList.remove('is-loading');
      if (this.publicState?.room_meta) {
        const meta = this.publicState.room_meta;
        const active = getActivePlayers(this.players || []);
        this.dom.btnStartMatch.disabled = active.length < (meta.min_players || 1);
      } else {
        this.dom.btnStartMatch.disabled = false;
      }
    }
    const joinSubmitBtn = this.dom.btnJoinSubmit || this.dom.modalJoinForm?.querySelector('button[type="submit"]');
    if (joinSubmitBtn) {
      joinSubmitBtn.disabled = false;
      joinSubmitBtn.classList.remove('is-loading');
    }
  }

  _buildRoomRow(room) {
    const row = document.createElement('div');
    row.className = 'open-room-row';

    const meta = document.createElement('div');
    meta.className = 'open-room-meta';

    const code = document.createElement('span');
    code.className = 'room-code-pill';
    code.textContent = `#${room.room_code}`;

    const title = document.createElement('strong');
    title.textContent = room.title;

    const diff = this._normalizeDifficulty(room.difficulty || 'mid');
    const diffBadge = document.createElement('span');
    diffBadge.className = `room-diff-badge diff-${diff}`;
    diffBadge.textContent = diff.toUpperCase();

    const host = document.createElement('span');
    host.textContent = `HOST: ${room.host} · ${room.player_count}/${room.max_players}`;
    meta.append(code, title, diffBadge, host);

    const joinBtn = document.createElement('button');
    joinBtn.type = 'button';
    joinBtn.className = 'pill-btn pill-btn-sm';
    joinBtn.textContent = room.spectatable ? 'WATCH' : 'JOIN';
    joinBtn.addEventListener('click', () => {
      sound.click();
      this._closeModal(this.dom.modalQuickJoin, { restoreFocus: false });
      this._send({
        type: 'JOIN_ROOM',
        player_name: this.playerName,
        room_code: room.room_code,
        payload: {},
      });
    });

    row.append(meta, joinBtn);
    return row;
  }

  _renderPinnedHelp() {
    const show = this.helpPinned && this.currentView === 'arena' && Boolean(this.activeGameType);
    this.dom.pipHelpPanel.classList.toggle('hidden', !show);
    this.dom.btnPinHelp.textContent = this.helpPinned ? 'HELP PINNED' : 'PIN HELP';
    if (!show) return;

    const hub = GAME_HUB_META[this.activeGameType] || {};
    this.dom.pipHelpBody.innerHTML = '';
    const summaryEl = document.createElement('div');
    summaryEl.className = 'pip-controls-summary';
    summaryEl.textContent = hub.controls || '';
    this.dom.pipHelpBody.appendChild(summaryEl);

    for (const tip of hub.helpTips || []) {
      const card = document.createElement('div');
      card.className = 'help-card';
      const titleEl = document.createElement('div');
      titleEl.className = 'help-card-title';
      titleEl.textContent = tip.title;
      const bodyEl = document.createElement('div');
      bodyEl.className = 'help-card-body';
      bodyEl.textContent = tip.body;
      card.append(titleEl, bodyEl);
      this.dom.pipHelpBody.appendChild(card);
    }
  }

  _resetComms() {
    this.commsOpen = false;
    this._hasUnreadComms = false;
    this._seenChatKey = '';
    this._lastEventsSig = '';
    this._lastChatSig = '';
    if (this.dom.arenaCommsDrawer) {
      this.dom.arenaCommsDrawer.classList.add('is-collapsed');
    }
    if (this.dom.btnToggleComms) {
      this.dom.btnToggleComms.setAttribute('aria-expanded', 'false');
    }
    if (this.dom.commsUnreadDot) {
      this.dom.commsUnreadDot.classList.add('hidden');
    }
    if (this.dom.arenaEventsList) this.dom.arenaEventsList.innerHTML = '';
    if (this.dom.arenaChatList) this.dom.arenaChatList.innerHTML = '';
  }

  _toggleComms(forceState = null) {
    const next = forceState === null ? !this.commsOpen : Boolean(forceState);
    this.commsOpen = next;
    if (this.dom.arenaCommsDrawer) {
      this.dom.arenaCommsDrawer.classList.toggle('is-collapsed', !next);
    }
    if (this.dom.btnToggleComms) {
      this.dom.btnToggleComms.setAttribute('aria-expanded', String(next));
    }
    if (next) {
      this._hasUnreadComms = false;
      this.dom.commsUnreadDot?.classList.add('hidden');
      const chat = this.publicState?.room_meta?.chat || [];
      if (chat.length) {
        const last = chat[chat.length - 1];
        this._seenChatKey = `${last.sender_id}:${last.ts}:${last.text}`;
      }
      if (this.dom.arenaEventsList) {
        this.dom.arenaEventsList.scrollTop = this.dom.arenaEventsList.scrollHeight;
      }
      if (this.dom.arenaChatList) {
        this.dom.arenaChatList.scrollTop = this.dom.arenaChatList.scrollHeight;
      }
      this.dom.arenaChatInput?.focus();
    }
  }

  _renderArenaComms(meta) {
    const events = Array.isArray(meta.events) ? meta.events : [];
    const chat = Array.isArray(meta.chat) ? meta.chat : [];

    if (this.dom.arenaEventsList) {
      const evSig = events.map((ev) => `${ev.ts}|${ev.kind}|${ev.text}`).join('\n');
      if (evSig !== this._lastEventsSig) {
        this._lastEventsSig = evSig;
        this.dom.arenaEventsList.innerHTML = '';
        if (!events.length) {
          const empty = document.createElement('div');
          empty.className = 'log-entry';
          empty.textContent = 'No match events yet.';
          this.dom.arenaEventsList.appendChild(empty);
        } else {
          for (const ev of events) {
            const row = document.createElement('div');
            const kind = ev.kind === 'warn' ? 'kind-warn' : ev.kind === 'finish' ? 'kind-finish' : '';
            row.className = kind ? `log-entry ${kind}` : 'log-entry';
            row.textContent = String(ev.text || '');
            this.dom.arenaEventsList.appendChild(row);
          }
          this.dom.arenaEventsList.scrollTop = this.dom.arenaEventsList.scrollHeight;
        }
      }
    }

    if (this.dom.arenaChatList) {
      const chatSig = chat.map((m) => `${m.sender_id}|${m.ts}|${m.text}`).join('\n');
      if (chatSig !== this._lastChatSig) {
        this._lastChatSig = chatSig;
        this.dom.arenaChatList.innerHTML = '';
        if (!chat.length) {
          const empty = document.createElement('div');
          empty.className = 'log-entry';
          empty.textContent = 'Room chat quiet — say hello.';
          this.dom.arenaChatList.appendChild(empty);
        } else {
          for (const m of chat) {
            const row = document.createElement('div');
            row.className = 'chat-msg';
            const sender = document.createElement('span');
            sender.className = 'chat-sender';
            sender.textContent = `${m.sender || 'Player'}:`;
            const timeEl = document.createElement('span');
            timeEl.className = 'chat-time';
            const tsMs = Number(m.ts || 0) * 1000;
            timeEl.textContent = tsMs
              ? new Date(tsMs).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              : '';
            const textEl = document.createElement('span');
            textEl.className = 'chat-text';
            textEl.textContent = String(m.text || '');
            row.append(sender, timeEl, textEl);
            this.dom.arenaChatList.appendChild(row);
          }
          this.dom.arenaChatList.scrollTop = this.dom.arenaChatList.scrollHeight;
        }
      }
    }

    if (chat.length) {
      const last = chat[chat.length - 1];
      const lastKey = `${last.sender_id}:${last.ts}:${last.text}`;
      if (this.commsOpen) {
        this._seenChatKey = lastKey;
        this._hasUnreadComms = false;
      } else if (lastKey !== this._seenChatKey) {
        if (last.sender_id !== this.clientId) {
          this._hasUnreadComms = true;
        } else {
          this._seenChatKey = lastKey;
        }
      }
    }
    if (this.dom.commsUnreadDot) {
      this.dom.commsUnreadDot.classList.toggle('hidden', !this._hasUnreadComms || this.commsOpen);
    }
  }

  _leaveRoomToLobby() {
    this._clearRoomState();
    this._send({ type: 'LEAVE_ROOM', player_name: this.playerName, payload: {} });
    this._showView('lobby');
  }

  _renderArenaChrome() {
    const meta = this.publicState?.room_meta || {};
    this.dom.hudRoomCode.textContent = this.currentRoom || '------';
    this.dom.hudGameTitle.textContent = meta.title || this.activeGameType?.toUpperCase() || '';

    const me = this.players.find((p) => p.id === this.clientId);
    const isSpectator = me?.role === 'spectator';
    if (this.dom.arenaSpectatorBadge) {
      this.dom.arenaSpectatorBadge.classList.toggle('hidden', !isSpectator);
    }

    const turnId = this.publicState?.turn_player_id;
    const turnPlayer = this.players.find((p) => p.id === turnId);
    const isMyTurn = turnId && turnId === this.clientId;
    this.dom.hudTurnIndicator.classList.toggle('is-my-turn', Boolean(isMyTurn));
    if (meta.phase === 'waiting') {
      this.dom.hudTurnIndicator.textContent = 'STAGING';
    } else if (meta.phase === 'finished') {
      this.dom.hudTurnIndicator.textContent = 'COMPLETE';
    } else if (isMyTurn) {
      this.dom.hudTurnIndicator.textContent = 'YOUR TURN';
    } else if (turnPlayer) {
      this.dom.hudTurnIndicator.textContent = `${turnPlayer.name.toUpperCase()} TURN`;
    } else {
      this.dom.hudTurnIndicator.textContent = 'LIVE';
    }

    this.dom.hudPlayersStrip.innerHTML = '';
    for (const p of getActivePlayers(this.players)) {
      const chip = document.createElement('span');
      chip.className = 'hud-player-chip';
      if (p.id === turnId) chip.classList.add('active-turn');
      if (!p.connected) chip.classList.add('disconnected');
      chip.textContent = `${p.name}: ${p.score}`;
      this.dom.hudPlayersStrip.appendChild(chip);
    }

    this._renderArenaComms(meta);

    const isWaiting = meta.phase === 'waiting';
    this.dom.waitingBunker.classList.toggle('hidden', !isWaiting);
    this.dom.gameStage.classList.toggle('hidden', isWaiting);

    if (isWaiting) {
      this._renderWaitingBunker(meta);
    }
  }

  _renderWaitingBunker(meta) {
    const gameMeta = this.catalog.find((g) => g.game_type === this.activeGameType);
    this.dom.bunkerGameHeading.textContent = meta.title || 'MATCH STAGING';
    this.dom.bunkerRulesNote.textContent = gameMeta?.description || '';

    const activePlayers = getActivePlayers(this.players);
    this.dom.bunkerRoster.innerHTML = '';
    for (const p of activePlayers) {
      const li = document.createElement('li');
      const left = document.createElement('span');
      left.textContent = `${p.name}${p.id === this.clientId ? ' (YOU)' : ''}`;
      const right = document.createElement('span');
      right.textContent = p.is_host ? 'HOST' : p.is_bot ? 'AI BOT' : 'READY';
      li.append(left, right);
      this.dom.bunkerRoster.appendChild(li);
    }

    const myRecord = this.players.find((p) => p.id === this.clientId);
    const isSpectator = myRecord?.role === 'spectator';
    const me = activePlayers.find((p) => p.id === this.clientId);
    const isHost = Boolean(me?.is_host);
    const activeDiff = this._normalizeDifficulty(meta.settings?.difficulty || 'mid');
    const activeDiffUpper = activeDiff.toUpperCase();
    this.dom.bunkerHostControls.classList.toggle('hidden', !isHost);
    this.dom.bunkerGuestWait.classList.toggle('hidden', isHost);
    if (!isHost) {
      this.dom.bunkerGuestWait.textContent = isSpectator
        ? `Difficulty: ${activeDiffUpper} · Spectating room — waiting for host to launch...`
        : `Difficulty: ${activeDiffUpper} · Waiting for host to launch the match...`;
    }
    this.dom.bunkerBotControls.classList.toggle('hidden', !meta.supports_bots);
    this.dom.btnStartMatch.disabled = activePlayers.length < (meta.min_players || 1);

    const schema = GAME_SETTINGS_SCHEMA[this.activeGameType];
    if (schema && isHost) {
      this.dom.bunkerSettings.classList.remove('hidden');
      const schemaKey = `${this.activeGameType}:${schema.map((f) => f.key).join(',')}`;
      if (this._bunkerSchemaKey !== schemaKey || this.dom.bunkerSettings.children.length !== schema.length) {
        this._bunkerSchemaKey = schemaKey;
        this.dom.bunkerSettings.innerHTML = '';
        for (const field of schema) {
          const wrap = document.createElement('div');
          wrap.className = 'setting-field';
          const selectId = `bunker-setting-${field.key}`;
          const label = document.createElement('label');
          label.htmlFor = selectId;
          label.textContent = field.label;
          const select = document.createElement('select');
          select.id = selectId;
          select.name = field.key;
          select.className = 'setting-select';
          for (const opt of field.options) {
            const o = document.createElement('option');
            o.value = opt;
            o.textContent = opt.toUpperCase();
            select.appendChild(o);
          }
          select.addEventListener('change', () => {
            sound.click();
            const val = /^\d+$/.test(select.value) ? Number(select.value) : select.value;
            if (this.activeGameType === 'minesweeper' && field.key === 'difficulty' && val === 'custom') {
              const custom = this._getMinesCustomSettings();
              this.sendGameAction('update_settings', {
                difficulty: 'custom',
                width: custom.width,
                height: custom.height,
                rows: custom.height,
                cols: custom.width,
                mines: custom.booms,
                booms: custom.booms,
              });
            } else {
              this.sendGameAction('update_settings', { [field.key]: val });
            }
          });
          wrap.append(label, select);
          this.dom.bunkerSettings.appendChild(wrap);
        }
      }

      for (const field of schema) {
        const select = this.dom.bunkerSettings.querySelector(`#bunker-setting-${field.key}`);
        if (!select) continue;
        const rawVal = String(meta.settings?.[field.key] ?? field.options[0]);
        const currentVal = field.key === 'difficulty' ? this._normalizeDifficulty(rawVal) : rawVal;
        if (document.activeElement !== select && select.value !== currentVal) {
          select.value = currentVal;
        }
      }
    } else {
      this._bunkerSchemaKey = '';
      this.dom.bunkerSettings.classList.add('hidden');
    }

    const showBunkerCustomMines = Boolean(
      this.activeGameType === 'minesweeper' && isHost && activeDiff === 'custom'
    );
    if (this.dom.bunkerMinesCustomRow) {
      this.dom.bunkerMinesCustomRow.classList.toggle('hidden', !showBunkerCustomMines);
      if (showBunkerCustomMines) {
        const fallback = this._getMinesCustomSettings();
        const cw = Math.max(8, Math.min(36, Number(meta.settings?.width ?? meta.settings?.cols) || fallback.width));
        const ch = Math.max(8, Math.min(30, Number(meta.settings?.height ?? meta.settings?.rows) || fallback.height));
        const maxBooms = Math.min(1071, Math.max(1, cw * ch - 9));
        const cb = Math.max(1, Math.min(maxBooms, Number(meta.settings?.booms ?? meta.settings?.mines) || fallback.booms));
        if (this.dom.bunkerMsWidth && document.activeElement !== this.dom.bunkerMsWidth) {
          this.dom.bunkerMsWidth.value = String(cw);
        }
        if (this.dom.bunkerMsHeight && document.activeElement !== this.dom.bunkerMsHeight) {
          this.dom.bunkerMsHeight.value = String(ch);
        }
        if (this.dom.bunkerMsBooms) {
          this.dom.bunkerMsBooms.max = String(maxBooms);
          if (document.activeElement !== this.dom.bunkerMsBooms) {
            this.dom.bunkerMsBooms.value = String(cb);
          }
        }
      }
    }
  }

  async _mountGameModule(gameType) {
    if (this._mountingType === gameType && this._mountingPromise) {
      return this._mountingPromise;
    }
    this._destroyActiveGame();
    this._mountingType = gameType;
    this.dom.gameStage.innerHTML = '';
    const promise = (async () => {
      try {
        const mod = await import(`/js/games/${gameType}.js?v=${ASSET_VERSION}`);
        if (this.activeGameType !== gameType) return;
        this.activeGameModule = mod.mount(this.dom.gameStage, {
          sendAction: (action, data) => this.sendGameAction(action, data),
          sound,
          getPlayerId: () => this.clientId,
          getPlayers: () => this.players,
        });
        this._syncGameModule();
      } catch (err) {
        console.error(`Failed to mount game module ${gameType}:`, err);
        this._toast('Failed to load game module. Please try again.', true);
      } finally {
        if (this._mountingPromise === promise) {
          this._mountingPromise = null;
          this._mountingType = null;
        }
      }
    })();
    this._mountingPromise = promise;
    return promise;
  }

  _syncGameModule() {
    if (!this.activeGameType || this.publicState?.room_meta?.phase === 'waiting') return;
    if (!this.activeGameModule) {
      this._mountGameModule(this.activeGameType);
      return;
    }
    this.activeGameModule.update(this.publicState || {}, this.privateState || {}, this.players);
  }

  _destroyActiveGame() {
    this._mountingPromise = null;
    this._mountingType = null;
    if (this.activeGameModule && typeof this.activeGameModule.destroy === 'function') {
      this.activeGameModule.destroy();
    }
    this.activeGameModule = null;
    this.dom.gameStage.innerHTML = '';
  }

  _showGameOverModal(reason) {
    const winnerIds = new Set(this.publicState?.winner_ids || []);
    const meWon = winnerIds.has(this.clientId);
    if (meWon) sound.win();

    this.dom.gameoverHeadline.textContent =
      winnerIds.size === 0 ? 'DRAW' : meWon ? 'VICTORY' : 'MATCH OVER';
    this.dom.gameoverReason.textContent = reason || this.publicState?.win_reason || 'Match completed.';

    const standings = [...getActivePlayers(this.players)].sort(
      (a, b) => Number(winnerIds.has(b.id)) - Number(winnerIds.has(a.id)) || b.score - a.score
    );
    this.dom.gameoverStandings.innerHTML = '';
    for (const p of standings) {
      const row = document.createElement('div');
      row.className = 'standing-row';
      if (winnerIds.has(p.id)) row.classList.add('winner');
      const left = document.createElement('span');
      left.textContent = `${winnerIds.has(p.id) ? '★ ' : ''}${p.name}`;
      const right = document.createElement('span');
      right.textContent = `${p.score} PTS`;
      row.append(left, right);
      this.dom.gameoverStandings.appendChild(row);
    }

    const me = this.players.find((p) => p.id === this.clientId);
    const humanCount = getActivePlayers(this.players).filter((p) => !p.is_bot).length;
    const canRematch = Boolean(me && me.role !== 'spectator' && (me.is_host || humanCount <= 1));
    this.dom.btnRematch.classList.toggle('hidden', !canRematch);
    this._openModal(
      this.dom.modalGameover,
      canRematch ? this.dom.btnRematch : this.dom.btnGameoverLobby
    );
  }

  _renderLeaderboardModal(activeGame = null) {
    const keys = this.catalog.map((g) => g.game_type);
    const current = activeGame || keys[0] || 'snake';

    this.dom.leaderboardTabs.innerHTML = '';
    for (const g of this.catalog) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `filter-tab ${g.game_type === current ? 'active' : ''}`;
      btn.textContent = g.title.toUpperCase();
      btn.addEventListener('click', () => {
        sound.click();
        this._renderLeaderboardModal(g.game_type);
      });
      this.dom.leaderboardTabs.appendChild(btn);
    }

    const rows = this.leaderboard[current] || [];
    if (rows.length === 0) {
      this.dom.leaderboardTableWrap.innerHTML =
        '<p class="empty-ticker-msg">No recorded victories for this module yet.</p>';
      return;
    }

    const table = document.createElement('table');
    table.className = 'leaderboard-table';
    table.innerHTML = `
      <thead><tr><th>RANK</th><th>CALLSIGN</th><th>WINS</th><th>BEST SCORE</th><th>GAMES</th></tr></thead>
      <tbody></tbody>
    `;
    const tbody = table.querySelector('tbody');
    rows.forEach((row, i) => {
      const tr = document.createElement('tr');
      [`#${i + 1}`, row.name, row.wins, row.best_score, row.games].forEach((val) => {
        const td = document.createElement('td');
        td.textContent = String(val);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    this.dom.leaderboardTableWrap.innerHTML = '';
    this.dom.leaderboardTableWrap.appendChild(table);
  }

  _toast(message, isError = false) {
    if (!this.dom.toast) return;
    this.dom.toast.innerHTML = '';
    const textSpan = document.createElement('span');
    textSpan.className = 'toast-message';
    textSpan.textContent = message;

    const dismissBtn = document.createElement('button');
    dismissBtn.type = 'button';
    dismissBtn.className = 'toast-dismiss-btn';
    dismissBtn.setAttribute('aria-label', 'Dismiss notification');
    dismissBtn.textContent = '✕';
    dismissBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      clearTimeout(this.toastTimer);
      this.dom.toast.classList.add('hidden');
    });

    this.dom.toast.append(textSpan, dismissBtn);
    this.dom.toast.classList.toggle('is-error', isError);
    this.dom.toast.classList.remove('hidden');
    clearTimeout(this.toastTimer);
    this.toastTimer = setTimeout(() => {
      this.dom.toast.classList.add('hidden');
    }, 4000);
  }

  _bindChessEditorEvents() {
    this.chessEditorSymbols = {
      K: '♔', Q: '♕', R: '♖', B: '♗', N: '♘', P: '♙',
      k: '♚', q: '♛', r: '♜', b: '♝', n: '♞', p: '♟',
    };
    this.chessEditorBrush = 'Q';
    this.chessEditorBoard = this._chessStandardMatrix();

    if (this.dom.btnCloseChessEditor) {
      this.dom.btnCloseChessEditor.addEventListener('click', () => {
        sound.click();
        this._closeModal(this.dom.modalChessEditor);
      });
    }

    const bindBrushContainer = (el) => {
      if (!el) return;
      el.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-piece]');
        if (!btn) return;
        sound.tick();
        this.chessEditorBrush = btn.dataset.piece;
        this._renderChessEditorPaletteSelection();
      });
    };
    bindBrushContainer(this.dom.chessPaletteWhite);
    bindBrushContainer(this.dom.chessPaletteBlack);

    if (this.dom.btnChessBrushErase) {
      this.dom.btnChessBrushErase.addEventListener('click', () => {
        sound.tick();
        this.chessEditorBrush = '';
        this._renderChessEditorPaletteSelection();
      });
    }

    if (this.dom.btnChessPresetStd) {
      this.dom.btnChessPresetStd.addEventListener('click', () => {
        sound.click();
        this.chessEditorBoard = this._chessStandardMatrix();
        this._renderChessCustomEditor();
      });
    }

    if (this.dom.btnChessPresetKq) {
      this.dom.btnChessPresetKq.addEventListener('click', () => {
        sound.click();
        const b = Array.from({ length: 8 }, () => Array(8).fill(null));
        b[0][4] = 'k';
        b[6][3] = 'Q';
        b[7][4] = 'K';
        this.chessEditorBoard = b;
        this._renderChessCustomEditor();
      });
    }

    if (this.dom.btnChessPresetClear) {
      this.dom.btnChessPresetClear.addEventListener('click', () => {
        sound.click();
        const b = Array.from({ length: 8 }, () => Array(8).fill(null));
        b[0][4] = 'k';
        b[7][4] = 'K';
        this.chessEditorBoard = b;
        this._renderChessCustomEditor();
      });
    }

    const launchCustom = (solo) => {
      const check = this._validateCustomChessBoard(this.chessEditorBoard);
      if (!check.ok) {
        sound.error?.();
        this._toast(check.msg, true);
        return;
      }
      sound.click();
      this._closeModal(this.dom.modalChessEditor, { restoreFocus: false });
      const diff = this._getSelectedDifficulty('chess');
      this._launchActivity('chess', {
        solo,
        is_public: !solo,
        bot_count: solo ? 1 : 0,
        settings: {
          difficulty: diff,
          time_control: '5+0',
          custom_board: this.chessEditorBoard,
        },
      });
    };

    if (this.dom.btnLaunchCustomChess) {
      this.dom.btnLaunchCustomChess.addEventListener('click', () => launchCustom(true));
    }
    if (this.dom.btnHostCustomChess) {
      this.dom.btnHostCustomChess.addEventListener('click', () => launchCustom(false));
    }
  }

  _chessStandardMatrix() {
    return [
      ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
      ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
      [null, null, null, null, null, null, null, null],
      [null, null, null, null, null, null, null, null],
      [null, null, null, null, null, null, null, null],
      [null, null, null, null, null, null, null, null],
      ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
      ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
    ];
  }

  _openChessCustomEditor() {
    if (!this.chessEditorBoard) {
      this.chessEditorBoard = this._chessStandardMatrix();
    }
    this._renderChessCustomEditor();
    this._openModal(this.dom.modalChessEditor, this.dom.btnCloseChessEditor);
  }

  _renderChessEditorPaletteSelection() {
    const brush = this.chessEditorBrush;
    document.querySelectorAll('.chess-brush-btn').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.piece === brush);
    });
    if (this.dom.btnChessBrushErase) {
      this.dom.btnChessBrushErase.classList.toggle('active', brush === '');
    }
  }

  _validateCustomChessBoard(board) {
    let wK = 0;
    let bK = 0;
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 8; c++) {
        const p = board[r][c];
        if (!p) continue;
        if (p === 'K') wK++;
        if (p === 'k') bK++;
      }
    }
    if (wK !== 1) return { ok: false, msg: `Requires exactly 1 White King (found ${wK}).` };
    if (bK !== 1) return { ok: false, msg: `Requires exactly 1 Black King (found ${bK}).` };
    return { ok: true, msg: '✓ Ready to launch (1 White King, 1 Black King) — win by checkmate or capturing all rival pieces.' };
  }

  _renderChessCustomEditor() {
    const syms = this.chessEditorSymbols || {};
    if (this.dom.chessPaletteWhite && !this.dom.chessPaletteWhite.children.length) {
      ['K', 'Q', 'R', 'B', 'N', 'P'].forEach((pc) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'chess-brush-btn';
        btn.dataset.piece = pc;
        btn.textContent = syms[pc];
        btn.title = `White ${pc}`;
        this.dom.chessPaletteWhite.appendChild(btn);
      });
    }
    if (this.dom.chessPaletteBlack && !this.dom.chessPaletteBlack.children.length) {
      ['k', 'q', 'r', 'b', 'n', 'p'].forEach((pc) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'chess-brush-btn';
        btn.dataset.piece = pc;
        btn.textContent = syms[pc];
        btn.title = `Black ${pc}`;
        this.dom.chessPaletteBlack.appendChild(btn);
      });
    }

    if (this.dom.chessEditorGrid) {
      this.dom.chessEditorGrid.innerHTML = '';
      for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
          const sq = document.createElement('div');
          const isLight = (r + c) % 2 === 0;
          const piece = this.chessEditorBoard[r][c];
          sq.className = `chess-editor-sq ${isLight ? 'light' : 'dark'}`;
          if (piece) {
            sq.textContent = syms[piece] || '';
            sq.classList.add(piece === piece.toUpperCase() ? 'piece-white' : 'piece-black');
          }
          sq.addEventListener('click', () => {
            sound.tick();
            if (this.chessEditorBrush === '') {
              this.chessEditorBoard[r][c] = null;
            } else if (this.chessEditorBoard[r][c] === this.chessEditorBrush) {
              this.chessEditorBoard[r][c] = null;
            } else {
              this.chessEditorBoard[r][c] = this.chessEditorBrush;
            }
            this._renderChessCustomEditor();
          });
          this.dom.chessEditorGrid.appendChild(sq);
        }
      }
    }

    this._renderChessEditorPaletteSelection();

    if (this.dom.chessEditorStatus) {
      const res = this._validateCustomChessBoard(this.chessEditorBoard);
      this.dom.chessEditorStatus.textContent = res.msg;
      this.dom.chessEditorStatus.className = `chess-editor-status ${res.ok ? 'valid' : 'invalid'}`;
    }
  }
}

window.addEventListener('DOMContentLoaded', () => {
  new BroadcastApp();
});
