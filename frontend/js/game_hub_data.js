/**
 * Bespoke PS5-inspired Game Hub metadata, Activity Cards (deep-links + est. times),
 * Contextual Game Help guides, dramatic full-bleed SVG hero artwork, and 16:9 card thumbnails
 * rendered strictly in DESIGN.md's Void Black, Bone Cream, Ash Taupe, and Alarm Red palette.
 */

export const GAME_HUB_META = {
  explore: {
    shortTitle: 'Explore',
    estTime: '11 MODULES',
    badge: 'OFFICIAL BROADCAST FEED · LIVE',
    controls: 'Use ← / → Arrow Keys to Browse · Pick Difficulty/Category · Click Play',
    activities: [
      { id: 'exp_uno', gameType: 'uno', thumbIdx: 1, title: 'UNO: 4-PLAYER TABLE VS AI', sub: '108-card deck, +4 Wilds & UNO callouts', est: 'EST. 6 MIN', minPlayers: 2, maxPlayers: 6, defaultPlayers: 4, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 3, settings: {} },
      { id: 'exp_globe', gameType: 'globe', thumbIdx: 0, title: 'GLOBE: 4-MODE WORLD HUNT', sub: 'Name, Flag, Hints & Border Bridge', est: 'EST. 5 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { mode: 'mix', rounds: 8 } },
      { id: 'exp_chess', gameType: 'chess', thumbIdx: 0, title: 'CHESS: BLITZ 3+2 VS AI', sub: 'Tactical alpha-beta bot match', est: 'EST. 6 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: { time_control: '3+2' } },
      { id: 'exp_skru', gameType: 'skru', thumbIdx: 0, title: 'SKRU: 1V1 MEMORY DUEL', sub: '10s peek, swaps & Basra toss', est: 'EST. 4 MIN', minPlayers: 2, maxPlayers: 6, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: {} },
      { id: 'exp_monopoly', gameType: 'monopoly', thumbIdx: 1, title: 'MONOPOLY: 4-PLAYER TYCOON', sub: '15s live auctions & property trades', est: 'EST. 20 MIN', minPlayers: 2, maxPlayers: 6, defaultPlayers: 4, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 3, settings: {} },
      { id: 'exp_qa', gameType: 'qa_trivia', thumbIdx: 1, title: 'QA: WORLD ATLAS & TRIVIA', sub: 'Flags, capitals, IQ, science & history', est: 'EST. 4 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { category: 'All', rounds: 10 } },
    ],
    helpTips: [
      { title: 'INSTANT DEEP-LINKING', body: 'Click any bottom Activity Card to bypass staging menus and jump straight into a configured solo or bot match.' },
      { title: 'THEME & PINNED HELP', body: 'Inside any match, open Theme to customize your Liquid Glass accent color or click Pin Help to keep controls docked beside the board.' },
    ],
  },
  snake: {
    shortTitle: 'Snake',
    estTime: '2–5 MIN',
    badge: 'ARCADE · 1–8P',
    controls: 'WASD / Arrow Keys / On-Screen D-Pad',
    difficultyNotes: {
      easy: 'Easy: Relaxed tick speed (165ms) for steady classic control.',
      mid: 'Mid: Balanced arcade pace (125ms step interval).',
      hard: 'Hard: Rapid reflex pace (85ms step) with 15 pts per food.',
    },
    helpTips: [
      { title: 'MOVEMENT & QUEUEING', body: 'Use WASD, Arrow Keys, or the touch D-Pad. Rapid consecutive turns are queued to prevent accidental 180° self-collisions.' },
      { title: 'SCORE RACE RULES', body: 'In multiplayer rooms, all snakes race over a 90-second broadcast window. Last snake standing or highest score at timeout wins.' },
      { title: 'SERVER SYNC', body: 'Your snake runs at 6–12 ticks/sec locally depending on difficulty (165ms / 125ms / 85ms) while syncing telemetry every 200ms with anti-cheat rate checks.' },
    ],
    activities: [
      { id: 'solo_survival', title: 'SOLO CLASSIC SURVIVAL', sub: 'Endless 20×20 grid high-score run', est: 'EST. 3 MIN', minPlayers: 1, maxPlayers: 1, defaultPlayers: 1, supportsSolo: true, supportsHost: false, defaultMatchup: 'ai', solo: true, settings: {} },
      { id: 'multiplayer_race', title: '90S MULTIPLAYER RACE', sub: 'Host a public 2–8P broadcast race', est: 'EST. 2 MIN', minPlayers: 2, maxPlayers: 8, defaultPlayers: 2, supportsSolo: false, supportsHost: true, defaultMatchup: 'host', solo: false, settings: { duration: 90 } },
    ],
  },
  minesweeper: {
    shortTitle: 'Mines',
    estTime: '2–12 MIN',
    badge: 'ARCADE · 1–8P',
    controls: 'Left-Click Reveal · Right-Click / Flag Mode · Click Number to Chord',
    difficultyNotes: {
      easy: 'Easy: 9×9 grid with 10 hidden mines (beginner sweep).',
      mid: 'Mid: 16×16 standard minefield with 40 mines.',
      hard: 'Hard: Dense 30×16 endurance field with 99 mines.',
      custom: 'Custom: Manually configured grid dimensions and boom count.',
    },
    helpTips: [
      { title: 'SAFE FIRST CLICK', body: 'Your mine matrix is generated on the server after your first click, guaranteeing 0 adjacent mines on your opening tile.' },
      { title: 'CHORDING SHORTCUT', body: 'Once the flags around a revealed number match its value, click the number directly to reveal all remaining safe neighbors.' },
      { title: 'CUSTOM GRID & BOOMS', body: 'Freely set your own Width, Height, and Mine count for custom challenge configurations.' },
    ],
    activities: [
      { id: 'solo_beginner', thumbIdx: 0, title: 'BEGINNER SWEEP (9×9)', sub: '9×9 grid with 10 hidden mines', est: 'EST. 2 MIN', minPlayers: 1, maxPlayers: 1, defaultPlayers: 1, supportsSolo: true, supportsHost: false, defaultMatchup: 'ai', solo: true, settings: { difficulty: 'easy', width: 9, height: 9, booms: 10 } },
      { id: 'solo_intermediate', thumbIdx: 0, title: 'INTERMEDIATE SWEEP (16×16)', sub: '16×16 standard minefield with 40 mines', est: 'EST. 5 MIN', minPlayers: 1, maxPlayers: 1, defaultPlayers: 1, supportsSolo: true, supportsHost: false, defaultMatchup: 'ai', solo: true, settings: { difficulty: 'mid', width: 16, height: 16, booms: 40 } },
      { id: 'solo_expert', thumbIdx: 0, title: 'EXPERT SWEEP (30×16)', sub: 'Dense 30×16 endurance field with 99 mines', est: 'EST. 10 MIN', minPlayers: 1, maxPlayers: 1, defaultPlayers: 1, supportsSolo: true, supportsHost: false, defaultMatchup: 'ai', solo: true, settings: { difficulty: 'hard', width: 30, height: 16, booms: 99 } },
      { id: 'multiplayer_race', thumbIdx: 0, title: 'MINEFIELD RACE (2–8P)', sub: 'Synchronized multiplayer race with live progress', est: 'EST. 5 MIN', minPlayers: 2, maxPlayers: 8, defaultPlayers: 2, supportsSolo: false, supportsHost: true, defaultMatchup: 'host', solo: false, settings: { difficulty: 'mid' } },
    ],
  },
  chess: {
    shortTitle: 'Chess',
    estTime: '6–20 MIN',
    badge: 'STRATEGY · 2P + SPEC',
    controls: 'Click Piece → Click Legal Dot · Resign Anytime',
    difficultyNotes: {
      easy: 'Easy: Casual depth-1 AI that leaves occasional tactical openings.',
      mid: 'Mid: Balanced alpha-beta depth-2 engine with positional tables.',
      hard: 'Hard: Deep alpha-beta depth-3 search with capture/promotion ordering.',
    },
    helpTips: [
      { title: 'FULL TOURNAMENT RULES', body: 'Server validates castling (kingside/queenside), en passant, pawn promotion (Q/R/B/N), checkmate, stalemate, 50-move, threefold & insufficient material draws.' },
      { title: 'CUSTOM BOARD MODE', body: 'Place pieces freely anywhere (1 White King and 1 Black King required). Win by checkmate OR capturing all of your opponent’s non-king pieces.' },
      { title: 'AI OPPONENT', body: 'Bot uses alpha-beta search with piece-square evaluation. Board automatically flips when playing Black.' },
      { title: 'SPECTATORS WELCOME', body: 'Share your 6-character room code even after the match begins so spectators can watch live moves and clocks.' },
    ],
    activities: [
      { id: 'blitz_3_2', thumbIdx: 0, title: 'BLITZ 3+2 VS AI BOT', sub: 'Fast 3-minute clock with 2s increment', est: 'EST. 6 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: { time_control: '3+2' } },
      { id: 'rapid_5_0', thumbIdx: 1, title: 'RAPID 5+0 VS AI BOT', sub: 'Standard 5-minute tactical match', est: 'EST. 10 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: { time_control: '5+0' } },
      { id: 'host_2p', thumbIdx: 2, title: 'HOST 2P MATCH', sub: 'Open a public room for human rival', est: 'EST. 12 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'host', solo: false, settings: { time_control: '5+0' } },
      { id: 'custom_board', thumbIdx: 3, title: 'CUSTOM CHESS BOARD', sub: 'Free placement (1 King each) · Checkmate or capture all pieces', est: 'CUSTOM SETUP', action: 'custom_chess', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: { time_control: '5+0' } },
    ],
  },
  backgammon: {
    shortTitle: 'Tawla',
    estTime: '8–15 MIN',
    badge: 'STRATEGY · 3 MODES · 2P',
    controls: 'Roll 2d6 → Click Valid Source → Click Highlighted Point / Bear Off',
    difficultyNotes: {
      easy: 'Easy: Relaxed AI mixes random legal moves with light point checks.',
      mid: 'Mid: Tactical AI scores hits/pins, bearing-off, made points, and blot safety.',
      hard: 'Hard: Aggressive prime-builder prioritizes connected blocks and locking blots.',
    },
    helpTips: [
      { title: 'CLASSIC / FRANJIEH', body: 'Standard setup with 2, 5, 3, 5 checkers. Hitting a lone blot sends it to the central Bar for mandatory re-entry.' },
      { title: 'TAWLA 31 (طاولة 31)', body: 'All 15 checkers start stacked on your furthest point. No hitting allowed — even a single checker blocks a point.' },
      { title: 'MAHBOSA (المحبوسة)', body: 'No Bar hitting! Landing on a lone opponent checker pins (jails) it underneath until your pinning checkers move away.' },
    ],
    activities: [
      { id: 'classic', thumbIdx: 0, title: 'CLASSIC TAWLA VS AI', sub: 'Standard Franjieh with Bar hitting & re-entry', est: 'EST. 10 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: { mode: 'classic' } },
      { id: 'tawla_31', thumbIdx: 1, title: 'TAWLA 31 (طاولة 31)', sub: 'Single checker blocks · No Bar hitting', est: 'EST. 12 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: { mode: 'tawla_31' } },
      { id: 'mahbosa', thumbIdx: 2, title: 'MAHBOSA (المحبوسة)', sub: 'Pin & imprison rival blots underneath your stack', est: 'EST. 12 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: { mode: 'mahbosa' } },
      { id: 'host_tawla', thumbIdx: 3, title: 'HOST 2P TAWLA ROOM', sub: 'Challenge a friend with 2d6 server dice', est: 'EST. 12 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'host', solo: false, settings: { mode: 'classic' } },
    ],
  },
  dominoes: {
    shortTitle: 'Dominoes',
    estTime: '5–12 MIN',
    badge: 'TABLETOP · 2–4P',
    controls: 'Click Highlighted Tile → Pick Left/Right End · Draw/Pass When Stuck',
    difficultyNotes: {
      easy: 'Easy: AI plays casual legal tiles without hand-suit tracking.',
      mid: 'Mid: AI sheds highest pip tiles cleanly each turn.',
      hard: 'Hard: AI preserves open suit control in hand while shedding high pips.',
    },
    helpTips: [
      { title: 'HIDDEN BONEYARD', body: 'Each player is dealt 7 tiles in private state. Remaining Double-Six tiles stay hidden in the server boneyard.' },
      { title: 'DRAWING & PASSING', body: 'If you have no tile matching either open end, draw until playable. You can only pass once the boneyard is empty.' },
      { title: 'BLOCKED BOARD SCORING', body: 'If all players pass consecutively, the lowest remaining pip sum wins the round and collects opponents’ pips.' },
    ],
    activities: [
      { id: 'quick_50', thumbIdx: 0, title: 'QUICK 50-PT MATCH VS AI', sub: '1v1 Double-Six sprint to 50 points', est: 'EST. 5 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: { target_score: 50 } },
      { id: 'standard_100', thumbIdx: 1, title: '4-WAY TABLE VS 3 BOTS', sub: 'Full 4-player table to 100 points', est: 'EST. 10 MIN', minPlayers: 2, maxPlayers: 4, defaultPlayers: 4, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 3, settings: { target_score: 100 } },
      { id: 'host_table', thumbIdx: 2, title: 'HOST 2–4P TABLE', sub: 'Open multiplayer Dominoes room', est: 'EST. 8 MIN', minPlayers: 2, maxPlayers: 4, defaultPlayers: 4, supportsSolo: true, supportsHost: true, defaultMatchup: 'host', solo: false, settings: { target_score: 100 } },
    ],
  },
  ludo: {
    shortTitle: 'Ludo',
    estTime: '6–15 MIN',
    badge: 'TABLETOP · 2–4P',
    controls: 'Roll Die → Click Highlighted Token to Advance',
    difficultyNotes: {
      easy: 'Easy: Playful bots choose casual legal token advances.',
      mid: 'Mid: Smart bots prioritize captures, home finishes, and safe stars.',
      hard: 'Hard: Threat-aware bots dodge rival chasing dice & lock safe zones.',
    },
    helpTips: [
      { title: 'DEPLOY & BONUS ROLLS', body: 'Roll a 6 to move a token out of the yard. Rolling a 6, capturing a rival, or reaching Home grants a bonus roll.' },
      { title: 'TRIPLE-SIX PENALTY', body: 'Rolling three consecutive 6s immediately forfeits your turn without moving.' },
      { title: 'STARRED SAFE ZONES', body: 'Tokens resting on ★ squares or start tiles cannot be captured. Exact roll required to enter the central Home triangle.' },
    ],
    activities: [
      { id: 'duel_2p', thumbIdx: 0, title: 'DUEL VS 1 AI BOT', sub: 'Opposite-corner 1v1 Ludo sprint', est: 'EST. 6 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: {} },
      { id: 'chaos_4p', thumbIdx: 1, title: '4-CORNER CHAOS VS 3 BOTS', sub: 'Full Red, Green, Yellow, Blue race', est: 'EST. 12 MIN', minPlayers: 2, maxPlayers: 4, defaultPlayers: 4, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 3, settings: {} },
      { id: 'host_race', thumbIdx: 2, title: 'HOST MULTIPLAYER RACE', sub: 'Create a 2–4 player Ludo room', est: 'EST. 10 MIN', minPlayers: 2, maxPlayers: 4, defaultPlayers: 4, supportsSolo: true, supportsHost: true, defaultMatchup: 'host', solo: false, settings: {} },
    ],
  },
  skru: {
    shortTitle: 'Skru',
    estTime: '4–10 MIN',
    badge: 'CARD & PARTY · 2–6P',
    controls: 'Draw / Take Discard / Basra Toss / Call SKRU!',
    difficultyNotes: {
      easy: 'Easy: 12s opening peek; bots track half their hand & call SKRU conservatively.',
      mid: 'Mid: 10s opening peek; balanced bot memory and swap logic.',
      hard: 'Hard: 7s brief peek; sharp bot memory tracks discards & calls SKRU early.',
    },
    helpTips: [
      { title: 'ACTION CARD POWERS', body: '7 & 8: Peek 1 own card. 9 & 10: Peek 1 rival card. Jack: Blind Swap. King (Kaab Dayer): Peek both & optionally swap.' },
      { title: 'SPECIAL CARDS & BASRA', body: 'Red Skru = 0 pts. Green Skru = +25 pts. +20 Card = +20 pts. Match the top discard with Basra Toss to shed a card permanently (wrong guess draws +1 penalty!).' },
      { title: 'CALLING "SKRU!"', body: 'Call SKRU! at turn start to lock your grid; every rival gets 1 final turn before all cards flip. Lowest point total wins.' },
    ],
    activities: [
      { id: 'duel_2p', thumbIdx: 0, title: '1V1 VS AI BOT', sub: 'Fast memory duel with 10s peek phase', est: 'EST. 4 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: {} },
      { id: 'party_4p', thumbIdx: 1, title: '4-PLAYER PARTY VS 3 BOTS', sub: 'Chaotic swaps & Basra races', est: 'EST. 8 MIN', minPlayers: 2, maxPlayers: 4, defaultPlayers: 4, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 3, settings: {} },
      { id: 'host_table', thumbIdx: 2, title: 'HOST 2–6P SKRU TABLE', sub: 'Invite friends via room code', est: 'EST. 8 MIN', minPlayers: 2, maxPlayers: 6, defaultPlayers: 6, supportsSolo: true, supportsHost: true, defaultMatchup: 'host', solo: false, settings: {} },
    ],
  },
  uno: {
    shortTitle: 'UNO',
    estTime: '4–10 MIN',
    badge: 'CARD & PARTY · 2–6P + SPEC',
    controls: 'Click Matching Color/Symbol Card · Draw If Stuck · Call UNO! at 1–2 Cards',
    difficultyNotes: {
      easy: 'Easy: Casual bots pick random playable cards & often forget to shout UNO!',
      mid: 'Mid: Smart bots shed high-point cards & match their strongest color on Wilds.',
      hard: 'Hard: Sharp bots save Wilds, chain +2/+4 attacks on low hands, & catch uncalled UNOs!',
    },
    helpTips: [
      { title: 'ACTION & WILD CARDS', body: 'Skip & +2 skip the next seat. Reverse flips turn order (in 2P matches Reverse acts as Skip so you play again!). Wild & Wild +4 let you switch active color.' },
      { title: 'UNO! SHOUT & CATCH (+2)', body: 'Press CALL UNO! when dropping from 2 cards or while sitting on 1 card. Any opponent who catches an uncalled 1-card hand deals +2 penalty cards!' },
      { title: 'DRAW & IMMEDIATE PLAY', body: 'If you draw a matching card on your turn, you may immediately play it or choose Keep & Pass Turn.' },
    ],
    activities: [
      { id: 'duel_2p', thumbIdx: 0, title: '1V1 UNO DUEL VS AI', sub: 'Fast head-to-head classic UNO sprint', est: 'EST. 4 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: {} },
      { id: 'party_4p', thumbIdx: 1, title: '4-PLAYER UNO VS 3 BOTS', sub: 'Full clockwise/reverse action table', est: 'EST. 7 MIN', minPlayers: 2, maxPlayers: 4, defaultPlayers: 4, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 3, settings: {} },
      { id: 'host_party', thumbIdx: 2, title: 'HOST 2–6P UNO PARTY', sub: 'Open multiplayer UNO table with spectators', est: 'EST. 8 MIN', minPlayers: 2, maxPlayers: 6, defaultPlayers: 6, supportsSolo: true, supportsHost: true, defaultMatchup: 'host', solo: false, settings: {} },
    ],
  },
  qa_trivia: {
    shortTitle: 'QA',
    estTime: '3–7 MIN',
    badge: 'IQ & ATLAS QA · 1–16P',
    controls: 'Pick Category & Difficulty · Answer A–D Before Clock Ends · SVG Flags & 3-Clue Mysteries',
    difficultyNotes: {
      easy: 'Easy: 20s clock (24s Mystery) + top-65 recognizable countries.',
      mid: 'Mid: Balanced 15s clock (18s Mystery) across Trivia & all 197 nations.',
      hard: 'Hard: Blitz 10s clock (12s Mystery) + same-continent tricky distractors.',
    },
    helpTips: [
      { title: '9 SELECTABLE CATEGORIES', body: 'Pick All Mix, Atlas (6 country mechanics), Flags, War (battles & tactics), Logic IQ, Science, History, General Knowledge, or Tech on the Hero bar.' },
      { title: 'ATLAS 6-MODE & 3-CLUE MYSTERY', body: 'Atlas rounds cover SVG Flag ID, Capitals, Border Detective, Population & Size, Traits, and 3-Clue Mystery (1000 / 600 / 300 pts).' },
      { title: 'SPEED SCORING & ENCYCLOPEDIA', body: 'Fast answers earn up to 1,000 pts. Open the top-right World Encyclopedia icon anytime to study all 197 countries.' },
    ],
    activities: [
      { id: 'war_battles', thumbIdx: 0, title: 'WAR: BATTLES & DOCTRINE (10 Qs)', sub: 'Military history, WW1/WW2, tactics & commanders', est: 'EST. 4 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { category: 'War', rounds: 10 } },
      { id: 'all_mix', thumbIdx: 1, title: 'ALL MIX: ATLAS + TRIVIA (10 Qs)', sub: 'Balanced mix of world geography & trivia', est: 'EST. 4 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { category: 'All', rounds: 10 } },
      { id: 'world_atlas', thumbIdx: 2, title: 'WORLD ATLAS: ALL 6 MODES (12 Qs)', sub: 'Flags, capitals, borders, mystery & traits', est: 'EST. 5 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { category: 'Atlas', rounds: 12 } },
      { id: 'flags_197', thumbIdx: 3, title: 'FLAGS OF 197 NATIONS (10 Qs)', sub: 'Identify vector flags on the timer', est: 'EST. 3 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { category: 'Flags', rounds: 10 } },
      { id: 'logic_iq', thumbIdx: 4, title: 'LOGIC & PATTERN IQ (8 Qs)', sub: 'Deep-link directly into IQ brain test', est: 'EST. 3 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { category: 'Logic & Pattern IQ', rounds: 8 } },
      { id: 'science_sprint', thumbIdx: 5, title: 'SCIENCE SPRINT (8 Qs)', sub: 'Physics, biology & astronomy rapid fire', est: 'EST. 3 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { category: 'Science', rounds: 8 } },
      { id: 'party_showdown', thumbIdx: 6, title: 'HOST 16P QA SHOWDOWN', sub: 'Open live synchronized 16-player QA room', est: 'EST. 5 MIN', minPlayers: 2, maxPlayers: 16, defaultPlayers: 2, supportsSolo: false, supportsHost: true, defaultMatchup: 'host', solo: false, settings: { category: 'All', rounds: 10 } },
    ],
  },
  globe: {
    shortTitle: 'Globe',
    estTime: '4–8 MIN',
    badge: 'INTERACTIVE 3D MAP · 1–16P',
    controls: 'Drag to Rotate Globe · Scroll to Zoom · Toggle 3D Globe / 2D Map · Click Countries or Microstate Pins',
    difficultyNotes: {
      easy: 'Easy: Major nations focus, 7 attempts, & generous 55s / 35s timers.',
      mid: 'Mid: Full 197-country atlas, 6 attempts, & balanced 40s / 25s clocks.',
      hard: 'Hard: All 197 nations incl. microstates, only 4 tries, & 25s / 16s blitz.',
    },
    helpTips: [
      { title: 'MODE 1 & 2 · NAME & FLAG HUNT', body: 'Pinpoint nations from only their Name or Flag. Misses color the map by thermal distance with km & compass direction arrows (up to 6 guided tries).' },
      { title: 'MODE 3 · PROGRESSIVE HINTS', body: 'Read starter traits or unlock extra Population, Area Size, and Capital clues (-75 pts each) to deduce the target nation on the map.' },
      { title: 'MODE 4 · MINIMUM NATIONS BETWEEN', body: 'Compare two highlighted nations connected by a great-circle arc and submit the shortest number of intermediate land-border nations between them.' },
    ],
    activities: [
      { id: 'mix_rounds', thumbIdx: 0, title: 'ALL 4 MODES MIX (8 ROUNDS)', sub: 'Rotate Name, Flag, Hint & Border Bridge', est: 'EST. 5 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { mode: 'mix', rounds: 8 } },
      { id: 'name_hunt', thumbIdx: 1, title: 'MODE 1: LOCATE BY NAME', sub: 'Pure country geolocation challenge', est: 'EST. 4 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { mode: 'name', rounds: 8 } },
      { id: 'flag_hunt', thumbIdx: 2, title: 'MODE 2: FLAG PINPOINT', sub: 'Identify flags directly on the world map', est: 'EST. 4 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { mode: 'flag', rounds: 8 } },
      { id: 'hint_detective', thumbIdx: 3, title: 'MODE 3: HINT DETECTIVE', sub: 'Find nations from rich geographic traits', est: 'EST. 4 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { mode: 'hint', rounds: 8 } },
      { id: 'border_bridge', thumbIdx: 4, title: 'MODE 4: BORDER BRIDGE', sub: 'Minimum intermediate countries between two nations', est: 'EST. 4 MIN', minPlayers: 1, maxPlayers: 16, defaultPlayers: 1, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, settings: { mode: 'borders_between', rounds: 8 } },
      { id: 'host_race', thumbIdx: 5, title: 'HOST 16P GLOBE RACE', sub: 'Open multiplayer map hunting lobby', est: 'EST. 6 MIN', minPlayers: 2, maxPlayers: 16, defaultPlayers: 2, supportsSolo: false, supportsHost: true, defaultMatchup: 'host', solo: false, settings: { mode: 'mix', rounds: 8 } },
    ],
  },
  monopoly: {
    shortTitle: 'Monopoly',
    estTime: '12–25 MIN',
    badge: 'TABLETOP · 2–6P',
    controls: 'Roll 2d6 · Click Any Board Tile to Build/Mortgage · Propose Live Trades',
    difficultyNotes: {
      easy: 'Easy: $1,800 starting cash; cautious bots cap bids at 80% list price.',
      mid: 'Mid: Classic $1,500 treasury; balanced auctions & house building.',
      hard: 'Hard: Tight $1,200 start; aggressive bots bid up to 135% & build early.',
    },
    helpTips: [
      { title: '15S LIVE AUCTIONS', body: 'Passing on an unowned property immediately opens a 15-second multiplayer auction where anyone (including bots) can bid.' },
      { title: 'MONOPOLIES & EVEN BUILDING', body: 'Owning all tiles of a color set doubles unimproved rent and unlocks evenly distributed houses (up to 4) and hotels.' },
      { title: 'TRADES, MORTGAGES & DEBT', body: 'Trade cash and unimproved properties anytime. If rent exceeds cash, sell houses or mortgage properties (50%) to stay solvent.' },
    ],
    activities: [
      { id: 'duel_2p', thumbIdx: 0, title: '1V1 ECONOMY VS AI', sub: 'Fast head-to-head property duel', est: 'EST. 12 MIN', minPlayers: 2, maxPlayers: 2, defaultPlayers: 2, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 1, settings: {} },
      { id: 'tycoon_4p', thumbIdx: 1, title: '4-PLAYER TYCOON VS 3 BOTS', sub: 'Competitive auctions & multi-party trades', est: 'EST. 20 MIN', minPlayers: 2, maxPlayers: 4, defaultPlayers: 4, supportsSolo: true, supportsHost: true, defaultMatchup: 'ai', solo: true, botCount: 3, settings: {} },
      { id: 'host_table', thumbIdx: 2, title: 'HOST 2–6P MONOPOLY', sub: 'Open a multiplayer Monopoly room', est: 'EST. 25 MIN', minPlayers: 2, maxPlayers: 6, defaultPlayers: 6, supportsSolo: true, supportsHost: true, defaultMatchup: 'host', solo: false, settings: {} },
    ],
  },

  tic_tac_toe: {
    shortTitle: 'Tic-Tac-Toe',
    estTime: '2–6 MIN',
    badge: 'STRATEGY · 5 MODES · 1–2P',
    controls: 'Click Open Grid Cell · In Ultimate, Follow Target Sub-Board Indicator',
    difficultyNotes: {
      easy: 'Easy: Casual bot that chooses random open cells with occasional basic blocks.',
      mid: 'Mid: Tactical bot that blocks immediate 1-move wins and seizes open winning lines.',
      hard: 'Hard: Mathematically unbeatable Minimax AI (zero losses) for 3×3 & deep heuristic search for 4×4, 5×5, and Ultimate.',
    },
    helpTips: [
      {
        title: 'CLASSIC 3×3 & MISÈRE RULES',
        body: 'Classic: Align 3 marks in a row (horizontal, vertical, or diagonal) to win. Misère (inverse): Completing 3-in-a-row immediately loses the match, forcing defensive trap placement!'
      },
      {
        title: 'EXTENDED 4×4 & 5×5 GRIDS',
        body: 'Larger tactical battlegrounds requiring 4-in-a-row to win! 3-in-a-row does NOT win. On 5×5, sliding 4-streak lines open up rich offensive diagonals.'
      },
      {
        title: 'ULTIMATE TIC-TAC-TOE ROUTING',
        body: '9 nested 3×3 sub-boards! Your move within a sub-board dictates which sub-board your opponent must play in next. If the target sub-board is already won or full, free placement unlocks across all open sub-boards.'
      },
      {
        title: 'UNBEATABLE MINIMAX AI',
        body: 'On Classic 3×3, the Hard bot runs a minimax game-tree solver that guarantees zero losses (win or draw) against any player move.'
      },
    ],
    activities: [
      {
        id: 'classic_minimax',
        thumbIdx: 0,
        title: 'CLASSIC 3×3 VS MINIMAX AI',
        sub: 'Standard 3-in-a-row vs mathematically unbeatable AI',
        est: 'EST. 2 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'classic', grid_size: 3, difficulty: 'hard' },
      },
      {
        id: 'misere_duel',
        thumbIdx: 1,
        title: 'MISÈRE MODE (3-IN-A-ROW LOSES)',
        sub: 'Inverted win rule: force your rival to complete 3 marks',
        est: 'EST. 3 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'misere', grid_size: 3, difficulty: 'mid' },
      },
      {
        id: 'extended_4x4',
        thumbIdx: 2,
        title: 'EXTENDED 4×4 (4-IN-A-ROW)',
        sub: 'Expanded 16-cell board requiring 4-in-a-row to win',
        est: 'EST. 4 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'extended_4x4', grid_size: 4, difficulty: 'mid' },
      },
      {
        id: 'extended_5x5',
        thumbIdx: 3,
        title: 'EXTENDED 5×5 (4-IN-A-ROW)',
        sub: 'Tactical 25-cell grid with sliding 4-mark streaks',
        est: 'EST. 5 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'extended_5x5', grid_size: 5, difficulty: 'mid' },
      },
      {
        id: 'ultimate_ttt',
        thumbIdx: 4,
        title: 'ULTIMATE TIC-TAC-TOE',
        sub: '9 nested boards with opponent-dictated target routing',
        est: 'EST. 8 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'ultimate', difficulty: 'mid' },
      },
      {
        id: 'host_2p',
        thumbIdx: 0,
        title: 'HOST 2P MULTIPLAYER ROOM',
        sub: 'Challenge a friend online or pass-and-play locally',
        est: 'EST. 5 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'host',
        solo: false,
        settings: { mode: 'classic', grid_size: 3 },
      },
    ],
  },
  rock_paper_scissors: {
    title: 'ROCK PAPER SCISSORS',
    sub: 'Classic 3-Choice and RPS-Lizard-Spock across Best-of-3, Best-of-5, and Endless formats',
    tag: 'TACTICAL CLASH',
    difficulty: 'MODERATE',
    players: '2 PLAYERS',
    modes: [
      {
        id: 'rps_classic_bo3',
        thumbIdx: 0,
        title: 'CLASSIC BEST-OF-3',
        sub: 'Standard Rock-Paper-Scissors in first-to-2 match',
        est: 'EST. 3 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'classic', format: 'bo3', difficulty: 'mid' },
      },
      {
        id: 'rps_lizard_spock_bo5',
        thumbIdx: 1,
        title: 'RPS-LIZARD-SPOCK (5-CHOICE)',
        sub: 'Expanded 5-weapon cyclic graph in Best-of-5 format',
        est: 'EST. 5 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'lizard_spock', format: 'bo5', difficulty: 'mid' },
      },
      {
        id: 'rps_endless_streak',
        thumbIdx: 2,
        title: 'ENDLESS STREAK CHALLENGE',
        sub: 'Chain consecutive round victories against predictive AI',
        est: 'ENDLESS',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'classic', format: 'endless', difficulty: 'hard' },
      },
      {
        id: 'rps_host_duel',
        thumbIdx: 3,
        title: 'HOST 2P MULTIPLAYER ROOM',
        sub: 'Challenge a rival online or pass-and-play locally',
        est: 'EST. 4 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'host',
        solo: false,
        settings: { mode: 'classic', format: 'bo3' },
      },
    ],
  },
  connect4: {
    title: 'CONNECT 4',
    sub: 'Vertical disc drops with Classic (7x6), Pop Out mode, 5-in-a-Row (9x7), and Blitz Mode with 5s countdown timer',
    tag: 'STRATEGY DUEL',
    difficulty: 'MODERATE',
    players: '2 PLAYERS',
    modes: [
      {
        id: 'c4_classic_duel',
        thumbIdx: 0,
        title: 'CLASSIC 7×6 DUEL',
        sub: 'Drop discs vertically to connect four in a row',
        est: 'EST. 3–5 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'classic', difficulty: 'mid' },
      },
      {
        id: 'c4_pop_out',
        thumbIdx: 1,
        title: 'POP OUT MODE',
        sub: 'Drop from the top or pop your discs from the bottom row',
        est: 'EST. 4–6 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'pop_out', difficulty: 'mid' },
      },
      {
        id: 'c4_five_in_a_row',
        thumbIdx: 2,
        title: '5-IN-A-ROW (9×7)',
        sub: 'Expanded 9 columns by 7 rows requiring 5 discs to win',
        est: 'EST. 5–8 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'five_in_a_row', difficulty: 'mid' },
      },
      {
        id: 'c4_blitz_5s',
        thumbIdx: 3,
        title: 'BLITZ 5-SECOND TIMER',
        sub: 'Rapid-fire turns with strict 5s timer countdown',
        est: 'EST. 2–3 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'blitz', blitz_time: 5, difficulty: 'mid' },
      },
      {
        id: 'c4_host_room',
        thumbIdx: 4,
        title: 'HOST 2P MULTIPLAYER ROOM',
        sub: 'Challenge a friend online or pass-and-play locally',
        est: 'EST. 5 MIN',
        minPlayers: 2,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'host',
        solo: false,
        settings: { mode: 'classic' },
      },
    ],
  },
  playing_cards: {
    title: 'PLAYING CARDS',
    shortTitle: 'Playing Cards',
    sub: 'Authentic 52-card table featuring Blackjack (vs Dealer), War, Memory / Concentration, and High-Low streak multipliers',
    tag: 'CASINO & CARD ARCADE',
    difficulty: 'CASUAL TO HARD',
    players: '1–2 PLAYERS',
    estTime: '2–5 MIN',
    badge: 'CARDS · 4 MODES · 1–2P',
    controls: 'Click Cards to Flip / Action Buttons (Hit, Stand, Double, Split, Higher, Lower)',
    difficultyNotes: {
      easy: 'Easy: Friendly dealer and casual bot with relaxed play.',
      mid: 'Mid: Standard casino dealer draw rules and tactical AI.',
      hard: 'Hard: Expert AI with photographic card memory and sharp probability tracking.',
    },
    helpTips: [
      {
        title: 'BLACKJACK RULES & SPLIT',
        body: 'Draw cards trying to get closer to 21 than the dealer without busting. Pair of same-rank cards can be split into two hands. Double down to double your bet on initial cards.',
      },
      {
        title: 'WAR & TIE-BREAKER PILES',
        body: 'Higher card wins the battle (Ace high). Ties trigger War: 3 cards face-down and 1 face-up deciding card. Chained consecutive wars accumulate massive card pots!',
      },
      {
        title: 'MEMORY / CONCENTRATION',
        body: 'Flip 2 cards to find matching ranks. Matched pairs lock in face-up. Beat the clock and track your total moves.',
      },
      {
        title: 'HIGH-LOW STREAK LADDER',
        body: 'Predict whether the next card drawn is higher or lower. Equal rank preserves your streak (Push). Climb the multiplier ladder up to 50x and bank points!',
      },
    ],
    activities: [
      {
        id: 'cards_blackjack',
        thumbIdx: 0,
        title: 'BLACKJACK VS DEALER',
        sub: 'Hit, Stand, Double Down, Split & Dealer draws to 17',
        est: 'EST. 3 MIN',
        minPlayers: 1,
        maxPlayers: 2,
        defaultPlayers: 1,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        settings: { mode: 'blackjack', difficulty: 'mid' },
      },
      {
        id: 'cards_war',
        thumbIdx: 1,
        title: 'WAR 2-PLAYER BATTLE',
        sub: 'Click-to-flip battles with 3-card tie-breaker war piles',
        est: 'EST. 4 MIN',
        minPlayers: 1,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'war', difficulty: 'mid' },
      },
      {
        id: 'cards_memory',
        thumbIdx: 2,
        title: 'MEMORY / CONCENTRATION',
        sub: '3D card flipping, move tracking & timer challenge',
        est: 'EST. 3 MIN',
        minPlayers: 1,
        maxPlayers: 2,
        defaultPlayers: 1,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        settings: { mode: 'memory', grid_size: '4x4', pairs_count: 8, difficulty: 'mid' },
      },
      {
        id: 'cards_high_low',
        thumbIdx: 3,
        title: 'HIGH-LOW STREAK MULTIPLIER',
        sub: 'Higher or Lower guesses with 50x multiplier ladder & bank',
        est: 'EST. 2 MIN',
        minPlayers: 1,
        maxPlayers: 2,
        defaultPlayers: 1,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        settings: { mode: 'high_low', difficulty: 'mid' },
      },
    ],
    modes: [
      {
        id: 'cards_blackjack',
        thumbIdx: 0,
        title: 'BLACKJACK VS DEALER',
        sub: 'Hit, Stand, Double Down, Split & Dealer draws to 17',
        est: 'EST. 3 MIN',
        minPlayers: 1,
        maxPlayers: 2,
        defaultPlayers: 1,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        settings: { mode: 'blackjack', difficulty: 'mid' },
      },
      {
        id: 'cards_war',
        thumbIdx: 1,
        title: 'WAR 2-PLAYER BATTLE',
        sub: 'Click-to-flip battles with 3-card tie-breaker war piles',
        est: 'EST. 4 MIN',
        minPlayers: 1,
        maxPlayers: 2,
        defaultPlayers: 2,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        botCount: 1,
        settings: { mode: 'war', difficulty: 'mid' },
      },
      {
        id: 'cards_memory',
        thumbIdx: 2,
        title: 'MEMORY / CONCENTRATION',
        sub: '3D card flipping, move tracking & timer challenge',
        est: 'EST. 3 MIN',
        minPlayers: 1,
        maxPlayers: 2,
        defaultPlayers: 1,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        settings: { mode: 'memory', grid_size: '4x4', pairs_count: 8, difficulty: 'mid' },
      },
      {
        id: 'cards_high_low',
        thumbIdx: 3,
        title: 'HIGH-LOW STREAK MULTIPLIER',
        sub: 'Higher or Lower guesses with 50x multiplier ladder & bank',
        est: 'EST. 2 MIN',
        minPlayers: 1,
        maxPlayers: 2,
        defaultPlayers: 1,
        supportsSolo: true,
        supportsHost: true,
        defaultMatchup: 'ai',
        solo: true,
        settings: { mode: 'high_low', difficulty: 'mid' },
      },
    ],
  },
};

/**
 * Atmospheric full-viewport SVG hero artwork positioned center-right over #0a0a0a Void Canvas,
 * dynamically tinted by the user's personalized --accent color & dusk radial spotlight.
 */
export function renderGameHeroArt(gameType) {
  const glow = `<defs>
    <radialGradient id="heroSpot" cx="72%" cy="44%" r="52%">
      <stop offset="0%" stop-color="var(--accent)" stop-opacity="0.32"/>
      <stop offset="50%" stop-color="var(--accent)" stop-opacity="0.09"/>
      <stop offset="100%" stop-color="#0a0a0a" stop-opacity="0"/>
    </radialGradient>
    <pattern id="radarGrid" width="48" height="48" patternUnits="userSpaceOnUse">
      <path d="M 48 0 L 0 0 0 48" fill="none" stroke="var(--color-bone)" stroke-width="0.75" opacity="0.07"/>
      <circle cx="0" cy="0" r="1.5" fill="var(--color-bone)" opacity="0.16"/>
    </pattern>
  </defs>
  <rect width="1440" height="900" fill="url(#heroSpot)"/>
  <rect x="580" y="0" width="860" height="900" fill="url(#radarGrid)"/>`;

  switch (gameType) {
    case 'explore':
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <g transform="translate(1020,430)">
          <circle cx="0" cy="0" r="340" fill="none" stroke="var(--color-bone)" stroke-width="1" opacity="0.14"/>
          <circle cx="0" cy="0" r="280" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="4 6" opacity="0.42"/>
          <circle cx="0" cy="0" r="210" fill="none" stroke="var(--color-bone)" stroke-width="1" opacity="0.22"/>
          <circle cx="0" cy="0" r="140" fill="none" stroke="var(--accent)" stroke-width="2" stroke-dasharray="16 10" opacity="0.55"/>
          <circle cx="0" cy="0" r="70" fill="none" stroke="var(--color-bone)" stroke-width="1" opacity="0.3"/>
          ${Array.from({ length: 36 }, (_, i) => `<line x1="0" y1="-280" x2="0" y2="${i % 3 === 0 ? '-260' : '-272'}" stroke="${i % 9 === 0 ? 'var(--accent)' : 'var(--color-bone)'}" stroke-width="${i % 9 === 0 ? '2.5' : '1'}" opacity="${i % 9 === 0 ? '0.85' : '0.35'}" transform="rotate(${i * 10})"/>`).join('')}
          <polygon points="0,-190 22,-50 190,0 50,22 0,190 -22,50 -190,0 -50,-22" fill="var(--color-bone)" opacity="0.06"/>
          <polygon points="0,-140 16,-36 140,0 36,16 0,140 -16,36 -140,0 -36,-16" fill="var(--accent)" opacity="0.12"/>
          <g transform="rotate(-28)">
            <polygon points="0,-170 95,95 0,42" fill="var(--color-snow-white)" opacity="0.88"/>
            <polygon points="0,-170 -95,95 0,42" fill="var(--color-bone)" opacity="0.45"/>
            <polygon points="0,-135 55,65 0,28" fill="var(--accent)" opacity="0.95"/>
            <polygon points="0,-135 -55,65 0,28" fill="var(--accent)" opacity="0.65"/>
            <circle cx="0" cy="0" r="18" fill="rgba(16,16,20,0.9)" stroke="var(--accent)" stroke-width="3"/>
            <circle cx="0" cy="0" r="7" fill="var(--color-snow-white)"/>
          </g>
          <text x="0" y="-295" text-anchor="middle" fill="var(--accent)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="16" letter-spacing="2">000° NORTH</text>
          <text x="295" y="6" text-anchor="start" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="14" opacity="0.6">090°</text>
          <text x="0" y="310" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="14" opacity="0.6">180°</text>
          <text x="-295" y="6" text-anchor="end" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="14" opacity="0.6">270°</text>
        </g>
        <text x="760" y="810" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="12" letter-spacing="3" opacity="0.22">SYSTEM RUNTIME // 11 SIMULATION MODULES LOADED</text>
      </svg>`;

    case 'snake':
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <g opacity="0.22" stroke="var(--color-bone)" stroke-width="0.8">
          ${Array.from({ length: 12 }, (_, i) => `<line x1="${680 + i * 62}" y1="80" x2="${680 + i * 62}" y2="820"/>`).join('')}
          ${Array.from({ length: 13 }, (_, i) => `<line x1="680" y1="${80 + i * 62}" x2="1362" y2="${80 + i * 62}"/>`).join('')}
          ${[
          [804, 204], [928, 204], [1052, 204], [1176, 204],
          [804, 390], [928, 390], [1052, 390], [1176, 390],
          [804, 576], [928, 576], [1052, 576], [1176, 576]
        ].map(([cx, cy]) => `<circle cx="${cx}" cy="${cy}" r="3" fill="var(--accent)" opacity="0.65"/>`).join('')}
        </g>
        <path d="M680 120 V80 H720 M1322 80 H1362 V120 M1362 780 V820 H1322 M720 820 H680 V780" fill="none" stroke="var(--accent)" stroke-width="2.5" opacity="0.65"/>
        <path d="M520 700 H804 V452 H1052 V266 H1238" fill="none" stroke="var(--accent)" stroke-width="68" stroke-linecap="round" stroke-linejoin="round" opacity="0.12"/>
        <path d="M520 700 H804 V452 H1052 V266 H1238" fill="none" stroke="var(--color-bone)" stroke-width="44" stroke-linecap="round" stroke-linejoin="round" opacity="0.38"/>
        <path d="M520 700 H804 V452 H1052 V266 H1238" fill="none" stroke="var(--accent)" stroke-width="8" stroke-dasharray="18 12" stroke-linecap="round" stroke-linejoin="round" opacity="0.95"/>
        ${[
          [618, 700], [742, 700], [804, 638], [804, 514],
          [866, 452], [990, 452], [1052, 390], [1052, 328], [1145, 266]
        ].map(([px, py]) => `
          <g transform="translate(${px},${py})">
            <rect x="-16" y="-16" width="32" height="32" rx="8" fill="rgba(16,16,20,0.88)" stroke="var(--accent)" stroke-width="2"/>
            <circle cx="0" cy="0" r="4" fill="var(--color-snow-white)"/>
          </g>
        `).join('')}
        <g transform="translate(1238,266)">
          <path d="M-20 -28 L42 -22 L64 0 L42 22 L-20 28 Z" fill="var(--color-snow-white)" opacity="0.92"/>
          <path d="M-10 -20 L30 -15 L46 0 L30 15 L-10 20 Z" fill="rgba(16,16,20,0.9)"/>
          <ellipse cx="24" cy="-9" rx="7" ry="2.5" fill="var(--accent)" transform="rotate(-15 24 -9)"/>
          <ellipse cx="24" cy="9" rx="7" ry="2.5" fill="var(--accent)" transform="rotate(15 24 9)"/>
          <circle cx="26" cy="-9" r="1.5" fill="#fff"/>
          <circle cx="26" cy="9" r="1.5" fill="#fff"/>
          <path d="M64 0 H88 M88 0 L102 -12 M88 0 L102 12" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
        </g>
        <g transform="translate(1176,514)">
          <circle cx="0" cy="0" r="88" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="10 8" opacity="0.6"/>
          <circle cx="0" cy="0" r="114" fill="none" stroke="var(--color-bone)" stroke-width="1" stroke-dasharray="3 6" opacity="0.3"/>
          <circle cx="0" cy="0" r="58" fill="var(--accent)" opacity="0.18"/>
          <line x1="-98" y1="0" x2="-78" y2="0" stroke="var(--accent)" stroke-width="2.5"/>
          <line x1="78" y1="0" x2="98" y2="0" stroke="var(--accent)" stroke-width="2.5"/>
          <line x1="0" y1="-98" x2="0" y2="-78" stroke="var(--accent)" stroke-width="2.5"/>
          <line x1="0" y1="78" x2="0" y2="98" stroke="var(--accent)" stroke-width="2.5"/>
          <rect x="-32" y="-32" width="64" height="64" rx="20" fill="var(--accent)" opacity="0.95"/>
          <circle cx="-10" cy="-10" r="9" fill="#fff" opacity="0.8"/>
          <path d="M0 -32 C6 -50 20 -48 24 -40" fill="none" stroke="var(--color-snow-white)" stroke-width="3" stroke-linecap="round"/>
          <path d="M12 -42 Q28 -54 26 -38 Z" fill="var(--color-snow-white)"/>
          <text x="0" y="132" text-anchor="middle" fill="var(--accent)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="13" letter-spacing="2">TARGET ACQUIRED // +100 PTS</text>
        </g>
        <text x="700" y="810" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="12" letter-spacing="3" opacity="0.25">SNAKE · GRID STEP 85–165MS · REALTIME TELEMETRY</text>
      </svg>`;

    case 'minesweeper':
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <!-- Tactical Sonar Radar Grid -->
        <g transform="translate(1040,430)">
          <circle cx="0" cy="0" r="350" fill="none" stroke="var(--color-bone)" stroke-width="1" opacity="0.16"/>
          <circle cx="0" cy="0" r="270" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="8 6" opacity="0.38"/>
          <circle cx="0" cy="0" r="190" fill="none" stroke="var(--color-bone)" stroke-width="1" opacity="0.22"/>
          <circle cx="0" cy="0" r="110" fill="none" stroke="var(--accent)" stroke-width="2" opacity="0.48"/>
          <!-- Azimuth Degree Marks -->
          ${Array.from({ length: 36 }, (_, i) => `<line x1="0" y1="-350" x2="0" y2="${i % 3 === 0 ? '-332' : '-342'}" stroke="${i % 9 === 0 ? 'var(--accent)' : 'var(--color-bone)'}" stroke-width="${i % 9 === 0 ? '2' : '1'}" opacity="${i % 9 === 0 ? '0.75' : '0.28'}" transform="rotate(${i * 10})"/>`).join('')}
          <!-- Sweeping Radar Beam -->
          <polygon points="0,0 260,-240 350,-110" fill="var(--accent)" opacity="0.10"/>
          <line x1="0" y1="0" x2="330" y2="-120" stroke="var(--accent)" stroke-width="2.5" opacity="0.85"/>
          
          <!-- Authentic Naval Contact Mine in 3D Perspective -->
          <!-- 8 Heavy Detonation Horns with Knurled Collars & Copper Detonator Caps -->
          ${Array.from({ length: 8 }, (_, i) => `
            <g transform="rotate(${i * 45})">
              <!-- Reinforced Collar Sleeve -->
              <rect x="-10" y="-195" width="20" height="95" rx="4" fill="#27272A" stroke="var(--color-bone)" stroke-width="1" opacity="0.85"/>
              <rect x="-13" y="-135" width="26" height="12" rx="3" fill="#18181B" stroke="var(--accent)" stroke-width="1.5"/>
              <!-- Conical Detonator Horn -->
              <polygon points="-7,-195 7,-195 9,-120 -9,-120" fill="#3F3F46"/>
              <!-- Copper Detonator Tip -->
              <circle cx="0" cy="-195" r="9" fill="var(--accent)"/>
              <circle cx="0" cy="-195" r="4" fill="#FFFFFF"/>
              <!-- Safety Shear Wire -->
              <line x1="-12" y1="-170" x2="12" y2="-170" stroke="rgba(255,255,255,0.4)" stroke-width="1.5"/>
            </g>
          `).join('')}

          <!-- Outer Spherical Armor Hull with Bolted Flange -->
          <circle cx="0" cy="0" r="115" fill="#18181B" stroke="var(--accent)" stroke-width="3.5" opacity="0.95"/>
          <circle cx="0" cy="0" r="98" fill="rgba(24,24,27,0.92)" stroke="var(--color-bone)" stroke-width="2" opacity="0.8"/>
          
          <!-- 16 Heavy Steel Armor Plate Perimeter Rivets -->
          ${Array.from({ length: 16 }, (_, i) => `<circle cx="${106 * Math.cos(i * Math.PI / 8)}" cy="${106 * Math.sin(i * Math.PI / 8)}" r="4.2" fill="#D4D4D8" stroke="#18181B" stroke-width="1.5"/>`).join('')}
          
          <!-- Equatorial Welded Seam Belt -->
          <ellipse cx="0" cy="0" rx="98" ry="18" fill="none" stroke="var(--accent)" stroke-width="2.5" opacity="0.7"/>
          <ellipse cx="0" cy="0" rx="98" ry="32" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1" stroke-dasharray="6 4"/>
          
          <!-- Center Pulsating Hazard Core (Warning Triangle & Detonator Strobe) -->
          <circle cx="0" cy="0" r="48" fill="rgba(var(--accent-rgb),0.25)" stroke="var(--accent)" stroke-width="2"/>
          <circle cx="0" cy="0" r="36" fill="var(--accent)" opacity="0.95"/>
          <circle cx="-12" cy="-12" r="9" fill="#FFF" opacity="0.85"/>
          <!-- Hazard Warning Triangle -->
          <polygon points="0,-18 18,14 -18,14" fill="#18181B" stroke="#FFF" stroke-width="1.5"/>
          <circle cx="0" cy="0" r="4" fill="var(--accent)"/>
          <line x1="0" y1="-8" x2="0" y2="-2" stroke="#FFF" stroke-width="2.5" stroke-linecap="round"/>
          <circle cx="0" cy="8" r="1.5" fill="#FFF"/>

          <!-- Top Lifting Shackle Eyelet -->
          <g transform="translate(0,-115)">
            <ellipse cx="0" cy="-12" rx="14" ry="16" fill="none" stroke="var(--color-bone)" stroke-width="5"/>
            <rect x="-8" y="-3" width="16" height="8" rx="2" fill="#27272A" stroke="var(--accent)" stroke-width="1.5"/>
          </g>
        </g>

        <!-- Tactical Numbered Matrix & Flag Banner -->
        <g transform="translate(700,220)">
          <rect x="0" y="0" width="68" height="68" rx="16" fill="rgba(16,16,20,0.85)" stroke="#3B82F6" stroke-width="2"/>
          <text x="34" y="47" text-anchor="middle" fill="#3B82F6" font-family="'DM Sans', sans-serif" font-weight="900" font-size="36">1</text>
        </g>
        <g transform="translate(784,220)">
          <rect x="0" y="0" width="68" height="68" rx="16" fill="rgba(16,16,20,0.85)" stroke="#10B981" stroke-width="2"/>
          <text x="34" y="47" text-anchor="middle" fill="#10B981" font-family="'DM Sans', sans-serif" font-weight="900" font-size="36">2</text>
        </g>
        <g transform="translate(868,220)">
          <rect x="0" y="0" width="68" height="68" rx="16" fill="rgba(16,16,20,0.85)" stroke="#EF4444" stroke-width="2"/>
          <text x="34" y="47" text-anchor="middle" fill="#EF4444" font-family="'DM Sans', sans-serif" font-weight="900" font-size="36">3</text>
        </g>
        <g transform="translate(700,304)">
          <rect x="0" y="0" width="68" height="68" rx="16" fill="var(--accent)" stroke="#FFF" stroke-width="2"/>
          <text x="34" y="48" text-anchor="middle" fill="#FFF" font-size="30">⚑</text>
        </g>
        
        <!-- Tactical Telemetry Caption -->
        <text x="700" y="810" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="12" letter-spacing="3" opacity="0.3">TACTICAL SWEEPER RADAR // ACOUSTIC &amp; MAGNETIC DETONATORS ARMED // MANUAL CHARGE CONFIGURATION</text>
      </svg>`;

    case 'chess':
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <!-- 3D Perspective Tournament Board -->
        <g transform="translate(640,240) skewX(-24) scale(0.95, 0.52)" opacity="0.18">
          ${Array.from({ length: 8 }, (_, r) =>
        Array.from({ length: 8 }, (_, c) =>
          (r + c) % 2 === 0
            ? `<rect x="${c * 86}" y="${r * 86}" width="86" height="86" rx="4" fill="var(--color-bone)"/>`
            : `<rect x="${c * 86}" y="${r * 86}" width="86" height="86" rx="4" fill="var(--accent)" opacity="0.6"/>`
        ).join('')
      ).join('')}
        </g>
        
        <!-- Tactical Threat Arcs and Coordinate Vectors -->
        <circle cx="1060" cy="420" r="280" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="14 8" opacity="0.45"/>
        <circle cx="1060" cy="420" r="360" fill="none" stroke="var(--color-bone)" stroke-width="1" opacity="0.18"/>
        
        <!-- Knight Attack Vector Laser Path (L-shape Nf3 -> e5) -->
        <path d="M1060 440 H860 V260" fill="none" stroke="var(--accent)" stroke-width="3" stroke-dasharray="8 6" opacity="0.8"/>
        <circle cx="860" cy="260" r="10" fill="var(--accent)" stroke="#fff" stroke-width="2"/>
        <text x="860" y="240" text-anchor="middle" fill="var(--accent)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="14">Nf3 × e5</text>
        
        <!-- Background Staunton King (with Cross Crown) -->
        <g transform="translate(770,160) scale(11)" opacity="0.28" stroke="var(--color-bone)" stroke-width="1.2">
          <path d="M9 39h27c0-3-1-4-2-4H11c-1 0-2 1-2 4z" fill="rgba(16,16,22,0.85)"/>
          <path d="M11 35c0-9 7-13 7-17 0-4-4-6-4-8 0-2 4-3 8.5-3s8.5 1 8.5 3c0 2-4 4-4 8 0 4 7 8 7 17z" fill="rgba(16,16,22,0.85)"/>
          <path d="M22.5 3v5M20 5.5h5" stroke="var(--accent)" stroke-width="1.5" stroke-linecap="round"/>
        </g>
        
        <!-- Background Staunton Rook (Castle Battlement) -->
        <g transform="translate(860,190) scale(10)" opacity="0.4" stroke="var(--color-bone)" stroke-width="1.2">
          <path d="M9 39h27c0-3-1-4-2-4H11c-1 0-2 1-2 4z" fill="rgba(16,16,22,0.85)"/>
          <path d="M12 35l1-19h19l1 19z" fill="rgba(16,16,22,0.85)"/>
          <path d="M9 16V9h5v3h6V9h6v3h5V9h5v7z" fill="rgba(16,16,22,0.85)"/>
          <rect x="21" y="20" width="3" height="8" rx="1" fill="var(--accent)"/>
        </g>
        
        <!-- Master Staunton Tournament Knight in Full Glory (Scale 14.5) -->
        <g transform="translate(930,130) scale(14.5)">
          <!-- Knight Pedestal Plinth with Liquid Glass Bevel -->
          <path d="M9 39h27c0-2-1-3-2-3H11c-1 0-2 1-2 3z" fill="rgba(20,20,28,0.95)" stroke="var(--color-bone)" stroke-width="1.2"/>
          <rect x="7" y="39" width="31" height="2" rx="0.5" fill="var(--accent)"/>
          
          <!-- Staunton Arched Neck and Chest -->
          <path d="M22 10C32.5 11 38.5 18 38 39H15C15 30 25 32.5 23 18" fill="rgba(18,18,26,0.95)" stroke="var(--color-bone)" stroke-width="1.2"/>
          
          <!-- Staunton Head, Ears, Muzzle and Chin -->
          <path d="M24 18c.38 2.91-5.55 7.37-8 9-3 2-2.82 4.34-5 4-1.04-.94 1.41-3.04 0-3-1 0 .19 1.23-1 2-1 0-4.003 1-4-4 0-2 6-12 6-12s1.89-1.9 2-3.5c-.73-.994-.5-2-.5-3 1-1 3 2.5 3 2.5h2s.78-1.992 2.5-3c1 0 1 3 1 3" fill="rgba(18,18,26,0.95)" stroke="var(--color-bone)" stroke-width="1.2"/>
          
          <!-- Almond Eye socket with glowing core -->
          <ellipse cx="14.8" cy="15.8" rx="1.6" ry="1" fill="var(--accent)" transform="rotate(30 14.8 15.8)"/>
          <circle cx="15.2" cy="15.8" r="0.6" fill="#fff"/>
          
          <!-- Nostril Cut -->
          <circle cx="9.2" cy="25.5" r="1" fill="var(--accent)"/>
          
          <!-- Elegant 3 Arched Mane Flutes -->
          <path d="M24.5 10.4c-.2 1.4.3 2.8 1.3 3.8" fill="none" stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round"/>
          <path d="M27.6 12c-.2 1.4.3 2.8 1.3 3.8" fill="none" stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round"/>
          <path d="M30.7 13.6c-.2 1.4.3 2.8 1.3 3.8" fill="none" stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round"/>
          
          <!-- Muzzle Highlight -->
          <path d="M6 24.5c.5-.5 1.5-.2 2.5.5" fill="none" stroke="var(--color-snow-white)" stroke-width="0.8" opacity="0.75" stroke-linecap="round"/>
        </g>
        
        <!-- HUD Telemetry Watermark -->
        <text x="720" y="810" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="12" letter-spacing="3" opacity="0.25">CHESS PROTOCOL · FIDE STANDARD · 1.e4 e5 2.Nf3 Nc6 3.Bc4</text>
      </svg>`;

    case 'backgammon':
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <g transform="translate(680,80)" opacity="0.32">
          ${Array.from({ length: 6 }, (_, i) => `
            <polygon points="${i * 115},0 ${57 + i * 115},360 ${115 + i * 115},0" fill="${i % 2 === 0 ? 'var(--color-bone)' : 'var(--accent)'}"/>
            <line x1="${57 + i * 115}" y1="0" x2="${57 + i * 115}" y2="360" stroke="#101014" stroke-width="2"/>
          `).join('')}
          ${Array.from({ length: 6 }, (_, i) => `
            <polygon points="${i * 115},740 ${57 + i * 115},380 ${115 + i * 115},740" fill="${i % 2 === 1 ? 'var(--color-bone)' : 'var(--accent)'}"/>
            <line x1="${57 + i * 115}" y1="740" x2="${57 + i * 115}" y2="380" stroke="#101014" stroke-width="2"/>
          `).join('')}
        </g>
        <g transform="translate(737,120)">
          ${[0, 48, 96, 144].map((offset) => `
            <g transform="translate(0,${offset})">
              <ellipse cx="0" cy="0" rx="46" ry="22" fill="var(--color-snow-white)" stroke="var(--color-bone)" stroke-width="3" opacity="0.88"/>
              <ellipse cx="0" cy="0" rx="32" ry="14" fill="none" stroke="var(--accent)" stroke-width="2"/>
            </g>
          `).join('')}
        </g>
        <g transform="translate(1082,540)">
          ${[0, -48, -96].map((offset) => `
            <g transform="translate(0,${offset})">
              <ellipse cx="0" cy="0" rx="46" ry="22" fill="var(--accent)" stroke="#fff" stroke-width="2.5" opacity="0.95"/>
              <ellipse cx="0" cy="0" rx="32" ry="14" fill="none" stroke="#fff" stroke-width="2" opacity="0.6"/>
            </g>
          `).join('')}
        </g>
        <g transform="translate(940,360) rotate(14)">
          <rect x="-65" y="-65" width="130" height="130" rx="28" fill="rgba(20,20,26,0.92)" stroke="var(--accent)" stroke-width="3.5"/>
          <circle cx="-34" cy="-34" r="11" fill="var(--accent)"/><circle cx="34" cy="-34" r="11" fill="var(--accent)"/>
          <circle cx="-34" cy="0" r="11" fill="var(--accent)"/><circle cx="34" cy="0" r="11" fill="var(--accent)"/>
          <circle cx="-34" cy="34" r="11" fill="var(--accent)"/><circle cx="34" cy="34" r="11" fill="var(--accent)"/>
        </g>
        <g transform="translate(1120,380) rotate(-16)">
          <rect x="-60" y="-60" width="120" height="120" rx="26" fill="var(--accent)" stroke="#fff" stroke-width="3"/>
          <circle cx="-30" cy="-30" r="10" fill="#fff"/><circle cx="30" cy="-30" r="10" fill="#fff"/>
          <circle cx="0" cy="0" r="10" fill="#fff"/>
          <circle cx="-30" cy="30" r="10" fill="#fff"/><circle cx="30" cy="30" r="10" fill="#fff"/>
        </g>
        <text x="720" y="810" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="12" letter-spacing="3" opacity="0.25">TAWLA PROTOCOL · 24 POINTS · DOUBLE-SIX BEARING OFF</text>
      </svg>`;

    case 'dominoes':
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <g transform="translate(820,180) rotate(-22)" opacity="0.35">
          <rect x="0" y="0" width="180" height="340" rx="24" fill="rgba(16,16,20,0.85)" stroke="var(--color-bone)" stroke-width="2.5"/>
          <line x1="15" y1="170" x2="165" y2="170" stroke="var(--color-bone)" stroke-width="2"/>
        </g>
        <g transform="translate(1140,240) rotate(16)" opacity="0.55">
          <rect x="0" y="0" width="190" height="360" rx="26" fill="rgba(18,18,24,0.9)" stroke="var(--accent)" stroke-width="3"/>
          <line x1="20" y1="180" x2="170" y2="180" stroke="var(--accent)" stroke-width="2.5"/>
          <circle cx="50" cy="50" r="14" fill="var(--accent)"/><circle cx="140" cy="50" r="14" fill="var(--accent)"/>
          <circle cx="95" cy="90" r="14" fill="var(--accent)"/>
          <circle cx="50" cy="130" r="14" fill="var(--accent)"/><circle cx="140" cy="130" r="14" fill="var(--accent)"/>
          <circle cx="50" cy="230" r="14" fill="var(--color-bone)"/><circle cx="140" cy="230" r="14" fill="var(--color-bone)"/>
          <circle cx="50" cy="310" r="14" fill="var(--color-bone)"/><circle cx="140" cy="310" r="14" fill="var(--color-bone)"/>
        </g>
        <g transform="translate(930,140) rotate(-6)">
          <rect x="-8" y="-8" width="236" height="436" rx="34" fill="rgba(0,0,0,0.7)"/>
          <rect x="0" y="0" width="220" height="420" rx="30" fill="var(--color-snow-white)" stroke="var(--accent)" stroke-width="4"/>
          <line x1="20" y1="210" x2="200" y2="210" stroke="#101014" stroke-width="4"/>
          <circle cx="110" cy="210" r="14" fill="var(--accent)" stroke="#fff" stroke-width="2"/>
          <circle cx="110" cy="210" r="5" fill="#fff"/>
          <circle cx="60" cy="55" r="16" fill="#101014"/><circle cx="160" cy="55" r="16" fill="#101014"/>
          <circle cx="60" cy="110" r="16" fill="#101014"/><circle cx="160" cy="110" r="16" fill="#101014"/>
          <circle cx="60" cy="165" r="16" fill="#101014"/><circle cx="160" cy="165" r="16" fill="#101014"/>
          <circle cx="60" cy="255" r="16" fill="var(--accent)"/><circle cx="160" cy="255" r="16" fill="var(--accent)"/>
          <circle cx="60" cy="310" r="16" fill="var(--accent)"/><circle cx="160" cy="310" r="16" fill="var(--accent)"/>
          <circle cx="60" cy="365" r="16" fill="var(--accent)"/><circle cx="160" cy="365" r="16" fill="var(--accent)"/>
        </g>
        <text x="720" y="810" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="12" letter-spacing="3" opacity="0.25">DOMINOES PROTOCOL · DOUBLE-SIX SET · BONEYARD DRAW SYSTEM</text>
      </svg>`;

    case 'ludo':
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <g transform="translate(800,100)" stroke="var(--color-bone)" stroke-width="2">
          <rect x="0" y="0" width="560" height="560" rx="32" fill="rgba(16,16,22,0.88)"/>
          <rect x="20" y="20" width="200" height="200" rx="22" fill="var(--accent)" opacity="0.35"/>
          <circle cx="80" cy="80" r="24" fill="var(--accent)"/><circle cx="160" cy="80" r="24" fill="var(--accent)"/>
          <circle cx="80" cy="160" r="24" fill="var(--accent)"/><circle cx="160" cy="160" r="24" fill="var(--accent)"/>
          <rect x="340" y="20" width="200" height="200" rx="22" fill="#3B82F6" opacity="0.25"/>
          <circle cx="400" cy="80" r="24" fill="#3B82F6"/><circle cx="480" cy="80" r="24" fill="#3B82F6"/>
          <circle cx="400" cy="160" r="24" fill="#3B82F6"/><circle cx="480" cy="160" r="24" fill="#3B82F6"/>
          <rect x="340" y="340" width="200" height="200" rx="22" fill="#F59E0B" opacity="0.25"/>
          <circle cx="400" cy="400" r="24" fill="#F59E0B"/><circle cx="480" cy="400" r="24" fill="#F59E0B"/>
          <circle cx="400" cy="480" r="24" fill="#F59E0B"/><circle cx="480" cy="480" r="24" fill="#F59E0B"/>
          <rect x="20" y="340" width="200" height="200" rx="22" fill="#10B981" opacity="0.25"/>
          <circle cx="80" cy="400" r="24" fill="#10B981"/><circle cx="160" cy="400" r="24" fill="#10B981"/>
          <circle cx="80" cy="480" r="24" fill="#10B981"/><circle cx="160" cy="480" r="24" fill="#10B981"/>
          <polygon points="220,220 280,280 220,340" fill="var(--accent)" opacity="0.85"/>
          <polygon points="340,220 280,280 340,340" fill="#F59E0B" opacity="0.85"/>
          <polygon points="220,220 280,280 340,220" fill="#3B82F6" opacity="0.85"/>
          <polygon points="220,340 280,280 340,340" fill="#10B981" opacity="0.85"/>
          <text x="250" y="110" fill="var(--accent)" font-size="34" text-anchor="middle">★</text>
          <text x="450" y="250" fill="#3B82F6" font-size="34" text-anchor="middle">★</text>
          <text x="310" y="470" fill="#F59E0B" font-size="34" text-anchor="middle">★</text>
          <text x="110" y="330" fill="#10B981" font-size="34" text-anchor="middle">★</text>
        </g>
        <g transform="translate(1080,480)">
          <ellipse cx="0" cy="110" rx="64" ry="24" fill="rgba(0,0,0,0.6)"/>
          <path d="M-55 100 C-50 70 -35 60 -24 30 H24 C35 60 50 70 55 100 Z" fill="var(--accent)" stroke="#fff" stroke-width="3"/>
          <rect x="-24" y="20" width="48" height="14" rx="6" fill="#fff"/>
          <circle cx="0" cy="-28" r="44" fill="var(--accent)" stroke="#fff" stroke-width="4"/>
          <circle cx="-14" cy="-42" r="12" fill="#fff" opacity="0.85"/>
        </g>
        <text x="720" y="810" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="12" letter-spacing="3" opacity="0.25">LUDO PROTOCOL · 4 YARDS · 4 SAFETY STARS · HOME RUN</text>
      </svg>`;

    case 'skru':
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <g opacity="0.22" transform="translate(720,120)">
          <rect x="0" y="0" width="160" height="230" rx="20" fill="var(--color-bone)"/>
          <rect x="180" y="0" width="160" height="230" rx="20" fill="var(--color-bone)"/>
          <rect x="0" y="250" width="160" height="230" rx="20" fill="var(--color-bone)"/>
          <rect x="180" y="250" width="160" height="230" rx="20" fill="var(--color-bone)"/>
        </g>
        <g transform="translate(860,180) rotate(-14)" opacity="0.75">
          <rect x="0" y="0" width="220" height="330" rx="26" fill="rgba(18,18,24,0.92)" stroke="var(--color-bone)" stroke-width="3"/>
          <rect x="16" y="16" width="188" height="298" rx="18" fill="none" stroke="rgba(255,255,255,0.18)" stroke-width="1.5"/>
          <path d="M40 165 C65 115 155 115 180 165 C155 215 65 215 40 165 Z" fill="none" stroke="var(--accent)" stroke-width="4"/>
          <circle cx="110" cy="165" r="28" fill="var(--accent)"/>
          <circle cx="110" cy="165" r="12" fill="#fff"/>
          <text x="110" y="260" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="24" letter-spacing="3">PEEK 7/8</text>
        </g>
        <g transform="translate(1040,140) rotate(10)">
          <rect x="-8" y="-8" width="256" height="376" rx="34" fill="rgba(0,0,0,0.65)"/>
          <rect x="0" y="0" width="240" height="360" rx="28" fill="var(--accent)" stroke="#fff" stroke-width="4.5"/>
          <rect x="14" y="14" width="212" height="332" rx="20" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="2"/>
          <path d="M70 70 L90 45 L120 70 L150 45 L170 70 H70 Z" fill="#fff"/>
          <circle cx="90" cy="40" r="5" fill="#fff"/><circle cx="120" cy="35" r="5" fill="#fff"/><circle cx="150" cy="40" r="5" fill="#fff"/>
          <ellipse cx="120" cy="195" rx="55" ry="75" fill="none" stroke="#fff" stroke-width="26"/>
          <ellipse cx="120" cy="195" rx="38" ry="58" fill="none" stroke="rgba(0,0,0,0.3)" stroke-width="4"/>
          <text x="36" y="55" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="900" font-size="34" text-anchor="middle">0</text>
          <text x="204" y="325" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="900" font-size="34" text-anchor="middle">0</text>
        </g>
        <text x="720" y="810" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="12" letter-spacing="3" opacity="0.25">SKRU PROTOCOL · 4 CARDS HIDDEN · 0 PT RED SCREW · BASRA +20</text>
      </svg>`;

    case 'uno':
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <g transform="translate(760,210) rotate(-18)" opacity="0.65">
          <rect x="0" y="0" width="220" height="330" rx="28" fill="#3B82F6" stroke="#fff" stroke-width="3"/>
          <ellipse cx="110" cy="165" rx="70" ry="105" fill="#101014" transform="rotate(24 110 165)"/>
          <path d="M80 140 C80 120 120 120 140 140 L155 125 M140 190 C140 210 100 210 80 190 L65 205" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round"/>
        </g>
        <g transform="translate(940,120) rotate(8)">
          <rect x="-8" y="-8" width="266" height="396" rx="36" fill="rgba(0,0,0,0.7)"/>
          <rect x="0" y="0" width="250" height="380" rx="30" fill="var(--accent)" stroke="#fff" stroke-width="4.5"/>
          <g transform="rotate(22 125 190)">
            <ellipse cx="125" cy="190" rx="84" ry="128" fill="#101014" stroke="rgba(255,255,255,0.5)" stroke-width="3"/>
            <path d="M125 190 L125 64 A84 128 0 0 1 206 190 Z" fill="#E5484D"/>
            <path d="M125 190 L206 190 A84 128 0 0 1 125 316 Z" fill="#3B82F6"/>
            <path d="M125 190 L125 316 A84 128 0 0 1 44 190 Z" fill="#10B981"/>
            <path d="M125 190 L44 190 A84 128 0 0 1 125 64 Z" fill="#F59E0B"/>
            <circle cx="125" cy="190" r="32" fill="#fff"/>
            <text x="125" y="202" fill="#101014" font-family="'DM Sans', sans-serif" font-weight="900" font-size="28" text-anchor="middle">UNO</text>
          </g>
          <text x="44" y="62" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="900" font-size="44" text-anchor="middle">+4</text>
          <text x="206" y="345" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="900" font-size="44" text-anchor="middle">+4</text>
        </g>
        <circle cx="1240" cy="320" r="32" fill="#E5484D" opacity="0.6"/>
        <circle cx="1280" cy="400" r="28" fill="#3B82F6" opacity="0.6"/>
        <circle cx="1230" cy="470" r="30" fill="#10B981" opacity="0.6"/>
        <circle cx="1170" cy="530" r="26" fill="#F59E0B" opacity="0.6"/>
        <text x="720" y="810" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="12" letter-spacing="3" opacity="0.25">UNO PROTOCOL · 108 CARDS · REVERSE · SKIP · WILD +4 · CALL UNO!</text>
      </svg>`;

    case 'qa_trivia':
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <g transform="translate(1040,430)">
          <circle cx="0" cy="0" r="300" fill="none" stroke="var(--color-bone)" stroke-width="1.5" opacity="0.22"/>
          <ellipse cx="0" cy="0" rx="140" ry="300" fill="none" stroke="var(--accent)" stroke-width="1.8" opacity="0.45"/>
          <ellipse cx="0" cy="0" rx="260" ry="300" fill="none" stroke="var(--color-bone)" stroke-width="1.2" opacity="0.25"/>
          <ellipse cx="0" cy="0" rx="300" ry="110" fill="none" stroke="var(--accent)" stroke-width="2" stroke-dasharray="14 10" opacity="0.55"/>
          <ellipse cx="0" cy="-120" rx="275" ry="70" fill="none" stroke="var(--color-bone)" stroke-width="1" opacity="0.2"/>
          <ellipse cx="0" cy="120" rx="275" ry="70" fill="none" stroke="var(--color-bone)" stroke-width="1" opacity="0.2"/>
          <circle cx="0" cy="0" r="360" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="8 6" opacity="0.35"/>
          <path d="M-180 220 C-100 280 100 280 180 220" fill="none" stroke="var(--accent)" stroke-width="4" stroke-linecap="round"/>
          <circle cx="0" cy="285" r="8" fill="var(--accent)"/>
          <g transform="translate(0,-305)">
            <polygon points="0,-24 7,-7 24,0 7,7 0,24 -7,7 -24,0 -7,-7" fill="var(--accent)"/>
          </g>
          <text x="0" y="105" text-anchor="middle" fill="var(--color-snow-white)" font-family="'DM Sans', sans-serif" font-weight="900" font-size="340" opacity="0.9" stroke="var(--accent)" stroke-width="4">?</text>
          <g transform="translate(-250,-120)">
            <circle cx="0" cy="0" r="32" fill="rgba(16,16,22,0.9)" stroke="var(--accent)" stroke-width="2"/>
            <text x="0" y="8" text-anchor="middle" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="700" font-size="14">ATLAS</text>
          </g>
          <g transform="translate(250,-120)">
            <circle cx="0" cy="0" r="32" fill="rgba(16,16,22,0.9)" stroke="var(--accent)" stroke-width="2"/>
            <text x="0" y="8" text-anchor="middle" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="700" font-size="14">FLAGS</text>
          </g>
          <g transform="translate(0,210)">
            <circle cx="0" cy="0" r="32" fill="var(--accent)" stroke="#fff" stroke-width="2"/>
            <text x="0" y="8" text-anchor="middle" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="700" font-size="14">WAR</text>
          </g>
          <g transform="translate(-270,80)">
            <circle cx="0" cy="0" r="32" fill="rgba(16,16,22,0.9)" stroke="var(--accent)" stroke-width="2"/>
            <text x="0" y="8" text-anchor="middle" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="700" font-size="14">LOGIC</text>
          </g>
          <g transform="translate(270,80)">
            <circle cx="0" cy="0" r="32" fill="rgba(16,16,22,0.9)" stroke="var(--accent)" stroke-width="2"/>
            <text x="0" y="8" text-anchor="middle" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="700" font-size="14">TECH</text>
          </g>
        </g>
        <text x="720" y="810" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="12" letter-spacing="3" opacity="0.25">QA PROTOCOL · 9 CATEGORIES · 197 NATIONS · 3-CLUE MYSTERY HUD</text>
      </svg>`;

    case 'globe':
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <g transform="translate(1040,430)">
          <circle cx="0" cy="0" r="330" fill="rgba(255,255,255,0.02)" stroke="var(--accent)" stroke-width="2.5" opacity="0.75"/>
          <circle cx="0" cy="0" r="350" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="8 6" opacity="0.45"/>
          <ellipse cx="0" cy="0" rx="140" ry="330" fill="none" stroke="var(--color-bone)" stroke-width="1.5" opacity="0.32"/>
          <ellipse cx="0" cy="0" rx="250" ry="330" fill="none" stroke="var(--color-bone)" stroke-width="1.2" opacity="0.22"/>
          <ellipse cx="0" cy="0" rx="330" ry="85" fill="none" stroke="var(--accent)" stroke-width="2" stroke-dasharray="14 10" opacity="0.6"/>
          <ellipse cx="0" cy="-140" rx="295" ry="60" fill="none" stroke="var(--color-bone)" stroke-width="1.2" opacity="0.25"/>
          <ellipse cx="0" cy="140" rx="295" ry="60" fill="none" stroke="var(--color-bone)" stroke-width="1.2" opacity="0.25"/>
          <path d="M-220 -80 C-200 -120 -150 -130 -130 -90 C-110 -50 -130 0 -110 50 C-90 100 -70 180 -100 230 C-130 200 -160 140 -160 80 C-160 30 -220 -20 -220 -80 Z" fill="var(--color-snow-white)" opacity="0.38"/>
          <path d="M-20 -180 C40 -200 120 -190 180 -140 C220 -90 200 -40 180 10 C160 60 120 100 130 170 C100 230 40 220 20 160 C0 100 -40 80 -40 0 C-40 -80 -70 -160 -20 -180 Z" fill="var(--color-snow-white)" opacity="0.45"/>
          <path d="M-140 -80 Q10 -220 160 -40" fill="none" stroke="var(--accent)" stroke-width="4" stroke-linecap="round" stroke-dasharray="12 8"/>
          <circle cx="-140" cy="-80" r="14" fill="#fff" stroke="var(--accent)" stroke-width="3"/>
          <circle cx="160" cy="-40" r="14" fill="var(--accent)" stroke="#fff" stroke-width="3"/>
          <g transform="translate(160,-40)">
            <circle cx="0" cy="0" r="44" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="6 4"/>
            <line x1="-54" y1="0" x2="-34" y2="0" stroke="var(--accent)" stroke-width="2.5"/>
            <line x1="34" y1="0" x2="54" y2="0" stroke="var(--accent)" stroke-width="2.5"/>
            <line x1="0" y1="-54" x2="0" y2="-34" stroke="var(--accent)" stroke-width="2.5"/>
            <line x1="0" y1="34" x2="0" y2="54" stroke="var(--accent)" stroke-width="2.5"/>
            <text x="0" y="74" text-anchor="middle" fill="var(--accent)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="13" letter-spacing="2">LOCKED: 53°54'N 27°34'E</text>
          </g>
        </g>
        <text x="720" y="810" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="12" letter-spacing="3" opacity="0.25">GLOBE PROTOCOL · 4 SEARCH MODES · HEATMAP GEOMETRY · BORDER BRIDGE</text>
      </svg>`;

    case 'monopoly':
    default:
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <g transform="translate(740,100)" fill="none" stroke="var(--color-bone)" stroke-width="2" opacity="0.32">
          <rect x="0" y="0" width="600" height="600" rx="32"/>
          <rect x="80" y="80" width="440" height="440" rx="20"/>
          <rect x="0" y="0" width="80" height="80" rx="16" fill="var(--accent)" opacity="0.75"/>
          <rect x="520" y="0" width="80" height="80" rx="16" fill="var(--color-bone)" opacity="0.45"/>
          <rect x="520" y="520" width="80" height="80" rx="16" fill="var(--accent)" opacity="0.75"/>
          <rect x="0" y="520" width="80" height="80" rx="16" fill="var(--color-bone)" opacity="0.45"/>
          ${Array.from({ length: 5 }, (_, i) => `<rect x="${90 + i * 84}" y="0" width="76" height="80" fill="var(--color-bone)" opacity="0.08"/>`).join('')}
          ${Array.from({ length: 5 }, (_, i) => `<rect x="${90 + i * 84}" y="520" width="76" height="80" fill="var(--color-bone)" opacity="0.08"/>`).join('')}
        </g>
        <g transform="translate(980,240) rotate(-10)">
          <path d="M-60 120 L-45 -80 H85 L100 120 Z" fill="rgba(18,18,24,0.96)" stroke="var(--color-bone)" stroke-width="3"/>
          <rect x="-56" y="70" width="152" height="40" fill="var(--accent)"/>
          <ellipse cx="20" cy="130" rx="140" ry="36" fill="rgba(22,22,30,0.98)" stroke="var(--color-bone)" stroke-width="3.5"/>
          <ellipse cx="20" cy="126" rx="110" ry="22" fill="none" stroke="var(--accent)" stroke-width="2"/>
        </g>
        <g transform="translate(1120,440)">
          <polygon points="0,-40 25,-60 50,-40" fill="#10B981"/>
          <rect x="0" y="-40" width="50" height="40" fill="#10B981" stroke="#fff" stroke-width="2"/>
          <polygon points="70,-40 95,-60 120,-40" fill="#10B981"/>
          <rect x="70" y="-40" width="50" height="40" fill="#10B981" stroke="#fff" stroke-width="2"/>
          <polygon points="140,-55 180,-85 220,-55" fill="var(--accent)"/>
          <rect x="140" y="-55" width="80" height="55" fill="var(--accent)" stroke="#fff" stroke-width="2.5"/>
          <rect x="195" y="-80" width="14" height="25" fill="var(--accent)" stroke="#fff" stroke-width="1.5"/>
        </g>
        <g transform="translate(1040,640)">
          <text x="0" y="0" text-anchor="middle" fill="var(--accent)" font-family="'DM Sans', sans-serif" font-weight="900" font-size="124" opacity="0.85">$1500</text>
        </g>
        <text x="720" y="810" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="600" font-size="12" letter-spacing="3" opacity="0.25">MONOPOLY PROTOCOL · 4-PLAYER TYCOON · AUCTIONS · TRADING · HOTELS</text>
      </svg>`;

    case 'tic_tac_toe':
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        ${glow}
        <!-- Isometric 3D Projection Grid Backdrop -->
        <g transform="translate(680, 220) skewX(-20) scale(0.9, 0.5)" opacity="0.22">
          <rect x="0" y="0" width="600" height="600" rx="16" fill="rgba(16,16,22,0.6)" stroke="var(--color-bone)" stroke-width="2"/>
          <line x1="200" y1="0" x2="200" y2="600" stroke="var(--accent)" stroke-width="3" stroke-dasharray="12 6"/>
          <line x1="400" y1="0" x2="400" y2="600" stroke="var(--accent)" stroke-width="3" stroke-dasharray="12 6"/>
          <line x1="0" y1="200" x2="600" y2="200" stroke="var(--accent)" stroke-width="3" stroke-dasharray="12 6"/>
          <line x1="0" y1="400" x2="600" y2="400" stroke="var(--accent)" stroke-width="3" stroke-dasharray="12 6"/>
          ${[0, 200, 400].map(gx => [0, 200, 400].map(gy => `
            <g transform="translate(${gx + 20}, ${gy + 20})">
              <line x1="53" y1="0" x2="53" y2="160" stroke="var(--color-bone)" stroke-width="0.8" opacity="0.3"/>
              <line x1="106" y1="0" x2="106" y2="160" stroke="var(--color-bone)" stroke-width="0.8" opacity="0.3"/>
              <line x1="0" y1="53" x2="160" y2="53" stroke="var(--color-bone)" stroke-width="0.8" opacity="0.3"/>
              <line x1="0" y1="106" x2="160" y2="106" stroke="var(--color-bone)" stroke-width="0.8" opacity="0.3"/>
            </g>
          `).join('')).join('')}
        </g>

        <!-- Tactical Target Radar Circle & Crosshairs -->
        <circle cx="1040" cy="450" r="320" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-dasharray="10 6" opacity="0.35"/>
        <circle cx="1040" cy="450" r="220" fill="none" stroke="var(--color-bone)" stroke-width="0.8" stroke-dasharray="4 8" opacity="0.2"/>
        <line x1="720" y1="450" x2="1360" y2="450" stroke="var(--accent)" stroke-width="0.8" opacity="0.2"/>
        <line x1="1040" y1="130" x2="1040" y2="770" stroke="var(--accent)" stroke-width="0.8" opacity="0.2"/>

        <!-- Dramatic Giant Neon 'X' Cross (Hero Foreground Left) -->
        <g transform="translate(860, 260)">
          <path d="M 0 0 L 140 140 M 140 0 L 0 140" stroke="var(--accent)" stroke-width="28" stroke-linecap="round" opacity="0.25"/>
          <path d="M 0 0 L 140 140 M 140 0 L 0 140" stroke="#0a0a0a" stroke-width="22" stroke-linecap="round"/>
          <path d="M 0 0 L 140 140 M 140 0 L 0 140" stroke="var(--accent)" stroke-width="8" stroke-linecap="round"/>
          <circle cx="70" cy="70" r="6" fill="#fff"/>
        </g>

        <!-- Dramatic Giant Neon 'O' Torus (Hero Foreground Right) -->
        <g transform="translate(1080, 360)">
          <circle cx="80" cy="80" r="75" fill="rgba(16,16,22,0.9)" stroke="var(--color-bone)" stroke-width="14" stroke-opacity="0.85"/>
          <circle cx="80" cy="80" r="75" fill="none" stroke="var(--accent)" stroke-width="4"/>
          <circle cx="80" cy="80" r="60" fill="none" stroke="var(--accent)" stroke-width="1" stroke-dasharray="4 6" opacity="0.6"/>
          <circle cx="80" cy="80" r="8" fill="var(--accent)"/>
        </g>

        <!-- Diagonal Winning Laser Strike Line with Terminal Spark Nodes -->
        <g transform="translate(760, 200)">
          <line x1="0" y1="360" x2="480" y2="0" stroke="var(--accent)" stroke-width="4" stroke-linecap="round"/>
          <line x1="0" y1="360" x2="480" y2="0" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
          <circle cx="0" cy="360" r="7" fill="var(--accent)" stroke="#fff" stroke-width="2"/>
          <circle cx="480" cy="0" r="7" fill="var(--accent)" stroke="#fff" stroke-width="2"/>
        </g>

        <!-- HUD Telemetry & Minimax Metadata -->
        <g transform="translate(780, 680)" font-family="'DM Sans', sans-serif" opacity="0.75">
          <rect x="0" y="0" width="280" height="36" rx="8" fill="rgba(20,20,28,0.8)" stroke="var(--color-hairline)"/>
          <circle cx="16" cy="18" r="4" fill="var(--accent)"/>
          <text x="30" y="22" fill="var(--color-bone)" font-size="12" font-weight="700" letter-spacing="1">MINIMAX 3×3 // UNBEATABLE SOLVER</text>
        </g>
      </svg>`;

    case 'rock_paper_scissors': {
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" fill="none">
        ${glow}
        <!-- Glowing Geometric Pentagram Graph in Perspective -->
        <g transform="translate(980, 420)">
          <!-- Ambient Concentric Orbit Rings -->
          <circle cx="0" cy="0" r="260" stroke="var(--color-bone)" stroke-width="0.8" stroke-dasharray="3 6" opacity="0.2"/>
          <circle cx="0" cy="0" r="180" stroke="var(--accent)" stroke-width="1.2" stroke-dasharray="6 8" opacity="0.45"/>
          <circle cx="0" cy="0" r="90" stroke="var(--color-bone)" stroke-width="0.6" opacity="0.15"/>

          <!-- 5 Pentagram Nodes & Chords -->
          <polygon points="0,-160 152,-49 94,130 -94,130 -152,-49" fill="rgba(16,16,22,0.6)" stroke="var(--accent)" stroke-width="2.5" stroke-opacity="0.8"/>
          <polygon points="0,-160 94,130 -152,-49 152,-49 -94,130" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="4 4" opacity="0.6"/>

          <!-- Node Markers -->
          <circle cx="0" cy="-160" r="18" fill="#18181B" stroke="var(--accent)" stroke-width="2"/>
          <circle cx="152" cy="-49" r="18" fill="#18181B" stroke="var(--color-snow-white)" stroke-width="2"/>
          <circle cx="94" cy="130" r="18" fill="#18181B" stroke="var(--accent)" stroke-width="2"/>
          <circle cx="-94" cy="130" r="18" fill="#18181B" stroke="var(--color-snow-white)" stroke-width="2"/>
          <circle cx="-152" cy="-49" r="18" fill="#18181B" stroke="var(--accent)" stroke-width="2"/>
        </g>

        <!-- Clashing Neon Vector Hands (Hero Center) -->
        <g transform="translate(800, 320)">
          <!-- Left Clashing Fist -->
          <g transform="translate(-80, 0)">
            <circle cx="50" cy="50" r="65" fill="rgba(18,18,24,0.85)" stroke="var(--accent)" stroke-width="3"/>
            <path d="M30 46V38C30 35 32 33 35 33H55C60 33 64 37 64 42V56C64 62 58 66 52 66H42C34 66 28 60 28 52V46Z" fill="var(--accent)" opacity="0.9"/>
          </g>
          <!-- Energy Clash Spark -->
          <circle cx="50" cy="50" r="14" fill="#fff" filter="drop-shadow(0 0 12px var(--accent))"/>
          <line x1="50" y1="10" x2="50" y2="90" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
          <line x1="10" y1="50" x2="90" y2="50" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
          <!-- Right Clashing Scissors -->
          <g transform="translate(100, 0)">
            <circle cx="50" cy="50" r="65" fill="rgba(18,18,24,0.85)" stroke="var(--color-snow-white)" stroke-width="3"/>
            <path d="M40 30L60 52M60 30L40 52M42 56C42 62 48 66 54 66H60" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
          </g>
        </g>

        <!-- HUD Telemetry & Cyclic Graph Metadata -->
        <g transform="translate(780, 680)" font-family="'DM Sans', sans-serif" opacity="0.8">
          <rect x="0" y="0" width="340" height="36" rx="8" fill="rgba(20,20,28,0.85)" stroke="var(--color-hairline)"/>
          <circle cx="16" cy="18" r="4" fill="var(--accent)"/>
          <text x="30" y="22" fill="var(--color-bone)" font-size="12" font-weight="700" letter-spacing="1">CYCLIC GRAPH // 5-CHOICE LIZARD-SPOCK</text>
        </g>
      </svg>`;
    }

    case 'connect4': {
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" fill="none">
        ${glow}
        <!-- Isometric Liquid Glass Cabinet in Perspective -->
        <g transform="translate(760, 260) skewY(-6) scale(0.9, 0.9)">
          <!-- Glass Cabinet Shell -->
          <rect x="0" y="0" width="540" height="460" rx="24" fill="rgba(18,22,34,0.85)" stroke="var(--color-hairline)" stroke-width="2"/>
          <rect x="12" y="12" width="516" height="436" rx="18" fill="rgba(24,28,42,0.6)" stroke="rgba(255,255,255,0.1)" stroke-width="1.2"/>

          <!-- Grid of Cutout Circular Slots -->
          ${[0, 1, 2, 3, 4, 5, 6].map(c => [0, 1, 2, 3, 4, 5].map(r => `
            <circle cx="${45 + c * 75}" cy="${46 + r * 74}" r="27" fill="#08090e" stroke="rgba(255,255,255,0.08)" stroke-width="1.5"/>
          `).join('')).join('')}

          <!-- Glowing 3D Discs Falling & Connected -->
          <!-- Red 4-Streak -->
          <circle cx="120" cy="416" r="25" fill="#ff4034" filter="drop-shadow(0 0 12px rgba(255,64,52,0.8))"/>
          <circle cx="195" cy="342" r="25" fill="#ff4034" filter="drop-shadow(0 0 12px rgba(255,64,52,0.8))"/>
          <circle cx="270" cy="268" r="25" fill="#ff4034" filter="drop-shadow(0 0 12px rgba(255,64,52,0.8))"/>
          <circle cx="345" cy="194" r="25" fill="#ff4034" filter="drop-shadow(0 0 16px rgba(255,64,52,0.9))"/>

          <!-- Yellow Rival Discs -->
          <circle cx="120" cy="342" r="25" fill="#facc15" filter="drop-shadow(0 0 10px rgba(250,204,21,0.7))"/>
          <circle cx="195" cy="416" r="25" fill="#facc15" filter="drop-shadow(0 0 10px rgba(250,204,21,0.7))"/>
          <circle cx="270" cy="342" r="25" fill="#facc15" filter="drop-shadow(0 0 10px rgba(250,204,21,0.7))"/>
          <circle cx="270" cy="416" r="25" fill="#facc15" filter="drop-shadow(0 0 10px rgba(250,204,21,0.7))"/>
          <circle cx="345" cy="416" r="25" fill="#facc15" filter="drop-shadow(0 0 10px rgba(250,204,21,0.7))"/>
          <circle cx="345" cy="342" r="25" fill="#ff4034" filter="drop-shadow(0 0 10px rgba(255,64,52,0.7))"/>
          <circle cx="345" cy="268" r="25" fill="#facc15" filter="drop-shadow(0 0 10px rgba(250,204,21,0.7))"/>

          <!-- Laser Connecting Slash Line -->
          <line x1="120" y1="416" x2="345" y2="194" stroke="#ff4034" stroke-width="4.5" stroke-linecap="round" filter="drop-shadow(0 0 14px rgba(255,64,52,0.9))"/>
        </g>

        <!-- Ambient Concentric Orbit Rings -->
        <g transform="translate(1030, 480)" opacity="0.4">
          <circle cx="0" cy="0" r="320" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-dasharray="8 6"/>
          <circle cx="0" cy="0" r="220" fill="none" stroke="var(--color-bone)" stroke-width="0.8" stroke-dasharray="4 8"/>
        </g>

        <!-- HUD Telemetry Metadata -->
        <g transform="translate(760, 720)" font-family="'DM Sans', sans-serif" opacity="0.85">
          <rect x="0" y="0" width="360" height="36" rx="8" fill="rgba(20,24,36,0.85)" stroke="var(--color-hairline)"/>
          <circle cx="16" cy="18" r="4" fill="var(--accent)"/>
          <text x="30" y="22" fill="var(--color-bone)" font-size="12" font-weight="700" letter-spacing="1">VERTICAL DISC STACK // 4-IN-A-ROW</text>
        </g>
      </svg>`;
    }

    case 'playing_cards': {
      return `<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" fill="none">
        ${glow}
        <!-- Holographic Playing Cards in Dynamic Perspective -->
        <g transform="translate(820, 260) skewY(-5) scale(0.95, 0.95)">
          <!-- Card Back 1 (Rotated) -->
          <g transform="translate(40, 60) rotate(-14)">
            <rect x="0" y="0" width="180" height="260" rx="14" fill="#0d0d14" stroke="rgba(255,255,255,0.18)" stroke-width="2"/>
            <rect x="10" y="10" width="160" height="240" rx="10" fill="#14141e" stroke="var(--accent)" stroke-width="1.2" stroke-dasharray="4 3"/>
            <circle cx="90" cy="130" r="32" fill="#1a1a28" stroke="var(--accent)" stroke-width="1.5"/>
            <text x="90" y="138" text-anchor="middle" fill="var(--accent)" font-family="'DM Sans', sans-serif" font-weight="900" font-size="24">🂠</text>
          </g>

          <!-- Ace of Spades (Hero Face Card) -->
          <g transform="translate(180, 40) rotate(6)" filter="drop-shadow(0 12px 28px rgba(0,0,0,0.7))">
            <rect x="0" y="0" width="190" height="270" rx="14" fill="#181822" stroke="rgba(255,255,255,0.2)" stroke-width="2"/>
            <text x="24" y="38" fill="#38bdf8" font-family="'DM Sans', sans-serif" font-weight="900" font-size="24">A</text>
            <text x="24" y="58" fill="#38bdf8" font-size="16">♠</text>
            <circle cx="95" cy="135" r="46" fill="rgba(56,189,248,0.08)" stroke="#38bdf8" stroke-width="1" stroke-dasharray="3 3"/>
            <path d="M95 100 C92 110 75 125 75 140 C75 150 83 158 93 158 C96 158 100 156 101 154 C99 160 93 168 87 170 H103 C97 168 91 160 89 154 C90 156 94 158 97 158 C107 158 115 150 115 140 C115 125 98 110 95 100 Z" fill="#38bdf8" filter="drop-shadow(0 0 16px rgba(56,189,248,0.7))"/>
            <text x="166" y="246" fill="#38bdf8" font-family="'DM Sans', sans-serif" font-weight="900" font-size="24" text-anchor="end">A</text>
            <text x="166" y="262" fill="#38bdf8" font-size="16" text-anchor="end">♠</text>
          </g>

          <!-- King of Hearts -->
          <g transform="translate(320, 80) rotate(18)" filter="drop-shadow(0 10px 24px rgba(0,0,0,0.6))">
            <rect x="0" y="0" width="180" height="260" rx="14" fill="#181822" stroke="rgba(255,255,255,0.18)" stroke-width="2"/>
            <text x="22" y="36" fill="#e5484d" font-family="'DM Sans', sans-serif" font-weight="900" font-size="22">K</text>
            <text x="22" y="54" fill="#e5484d" font-size="15">♥</text>
            <path d="M90 120 C76 100 60 114 60 128 C60 148 90 168 90 168 C90 168 120 148 120 128 C120 114 104 100 90 120 Z" fill="#e5484d" filter="drop-shadow(0 0 14px rgba(229,72,77,0.7))"/>
            <text x="158" y="238" fill="#e5484d" font-family="'DM Sans', sans-serif" font-weight="900" font-size="22" text-anchor="end">K</text>
          </g>

          <!-- Casino Chip Stacks -->
          <g transform="translate(140, 290)">
            <ellipse cx="0" cy="20" rx="36" ry="12" fill="#e5484d" stroke="#fff" stroke-width="1.5" stroke-dasharray="6 4"/>
            <ellipse cx="0" cy="12" rx="36" ry="12" fill="#f59e0b" stroke="#fff" stroke-width="1.5" stroke-dasharray="6 4"/>
            <ellipse cx="0" cy="4" rx="36" ry="12" fill="#38bdf8" stroke="#fff" stroke-width="1.5" stroke-dasharray="6 4"/>
            <ellipse cx="0" cy="-4" rx="36" ry="12" fill="#10b981" stroke="#fff" stroke-width="1.5" stroke-dasharray="6 4"/>
            <text x="0" y="0" text-anchor="middle" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="900" font-size="11">$100</text>
          </g>
        </g>

        <!-- Ambient Concentric Orbit Rings -->
        <g transform="translate(1030, 480)" opacity="0.4">
          <circle cx="0" cy="0" r="320" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-dasharray="8 6"/>
          <circle cx="0" cy="0" r="220" fill="none" stroke="var(--color-bone)" stroke-width="0.8" stroke-dasharray="4 8"/>
        </g>

        <!-- HUD Telemetry Metadata -->
        <g transform="translate(760, 720)" font-family="'DM Sans', sans-serif" opacity="0.85">
          <rect x="0" y="0" width="380" height="36" rx="8" fill="rgba(20,24,36,0.85)" stroke="var(--color-hairline)"/>
          <circle cx="16" cy="18" r="4" fill="var(--accent)"/>
          <text x="30" y="22" fill="var(--color-bone)" font-size="12" font-weight="700" letter-spacing="1">52-CARD SUITE // BLACKJACK · WAR · MEMORY</text>
        </g>
      </svg>`;
    }
  }
}

/**
 * Generates rich, highly detailed 16:9 translucent thumbnail SVG art for Liquid Glass Activity Cards.
 * Each game mode and index features bespoke, intricate game assets (Staunton Knight, articulated snake,
 * naval contact mine, Uno +4 cards, Monopoly 3D houses & dice, Ludo pawns, ivory dominoes, etc.).
 */
export function renderActivityThumb(gameType, idx = 0) {
  const generators = {
    // ------------------------------------------------------------------------
    // SNAKE
    // ------------------------------------------------------------------------
    snake: (i) => {
      if (i === 1) {
        // 90s Multiplayer race: Two articulated snakes racing for the golden star orb + timer HUD
        return `
          <!-- Cyberpunk Grid -->
          <path d="M 0 30 L 320 30 M 0 60 L 320 60 M 0 90 L 320 90 M 0 120 L 320 120" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
          <path d="M 50 0 L 50 180 M 110 0 L 110 180 M 170 0 L 170 180 M 230 0 L 230 180 M 290 0 L 290 180" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
          <!-- Snake 1 (Accent) -->
          <path d="M 30 75 L 100 75 Q 115 75 115 60 L 115 40 Q 115 25 130 25 L 170 25" fill="none" stroke="var(--accent)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="50" cy="75" r="3" fill="#FFF" opacity="0.5"/>
          <circle cx="80" cy="75" r="3" fill="#FFF" opacity="0.5"/>
          <circle cx="115" cy="50" r="3" fill="#FFF" opacity="0.5"/>
          <circle cx="145" cy="25" r="3" fill="#FFF" opacity="0.5"/>
          <g transform="translate(172, 25)">
            <rect x="-8" y="-7" width="16" height="14" rx="5" fill="var(--accent)"/>
            <circle cx="2" cy="-2.5" r="2.2" fill="#000"/>
            <circle cx="2" cy="2.5" r="2.2" fill="#000"/>
            <circle cx="2.5" cy="-2.8" r="0.8" fill="#FFF"/>
            <circle cx="2.5" cy="2.2" r="0.8" fill="#FFF"/>
            <path d="M 8 0 L 13 0 M 13 -2 L 15 0 L 13 2" stroke="#FF4D4D" stroke-width="1.4" stroke-linecap="round"/>
          </g>
          <!-- Snake 2 (Electric Cyan) -->
          <path d="M 50 105 L 140 105 Q 155 105 155 90 L 155 65 Q 155 50 170 50 L 195 50" fill="none" stroke="#38BDF8" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="70" cy="105" r="3" fill="#FFF" opacity="0.5"/>
          <circle cx="105" cy="105" r="3" fill="#FFF" opacity="0.5"/>
          <circle cx="155" cy="78" r="3" fill="#FFF" opacity="0.5"/>
          <g transform="translate(197, 50)">
            <rect x="-8" y="-7" width="16" height="14" rx="5" fill="#38BDF8"/>
            <circle cx="2" cy="-2.5" r="2.2" fill="#000"/>
            <circle cx="2" cy="2.5" r="2.2" fill="#000"/>
            <circle cx="2.5" cy="-2.8" r="0.8" fill="#FFF"/>
            <circle cx="2.5" cy="2.2" r="0.8" fill="#FFF"/>
            <path d="M 8 0 L 13 0 M 13 -2 L 15 0 L 13 2" stroke="#FF4D4D" stroke-width="1.4" stroke-linecap="round"/>
          </g>
          <!-- Contested Golden Star Orb -->
          <g transform="translate(230, 36)">
            <circle cx="0" cy="0" r="16" fill="rgba(245,158,11,0.2)"/>
            <circle cx="0" cy="0" r="10" fill="#F59E0B"/>
            <polygon points="0,-6 2,-2 6,-2 3,1 4,5 0,3 -4,5 -3,1 -6,-2 -2,-2" fill="#FFF"/>
          </g>
          <!-- Race Stopwatch HUD -->
          <g transform="translate(258, 14)">
            <rect x="0" y="0" width="50" height="24" rx="6" fill="rgba(16,16,20,0.75)" stroke="rgba(255,255,255,0.12)"/>
            <circle cx="12" cy="12" r="5" fill="none" stroke="var(--accent)" stroke-width="1.5"/>
            <line x1="12" y1="12" x2="12" y2="9" stroke="var(--accent)" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="12" y1="12" x2="14" y2="12" stroke="var(--accent)" stroke-width="1.5" stroke-linecap="round"/>
            <text x="22" y="16" fill="var(--color-snow-white)" font-family="'DM Sans',sans-serif" font-weight="700" font-size="10">90s</text>
          </g>
        `;
      }
      // Solo survival: Detailed winding snake with segmented scales, eyes, tongue, and neon glowing apple
      return `
        <!-- Cyberpunk Grid -->
        <path d="M 0 30 L 320 30 M 0 60 L 320 60 M 0 90 L 320 90 M 0 120 L 320 120" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
        <path d="M 50 0 L 50 180 M 110 0 L 110 180 M 170 0 L 170 180 M 230 0 L 230 180 M 290 0 L 290 180" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
        <!-- Soft Glow behind body -->
        <path d="M 30 95 L 110 95 Q 128 95 128 77 L 128 45 Q 128 25 148 25 L 210 25 Q 230 25 230 45 L 230 65" fill="none" stroke="var(--accent)" stroke-width="20" stroke-linecap="round" stroke-linejoin="round" opacity="0.16"/>
        <!-- Articulated Snake Body -->
        <path d="M 30 95 L 110 95 Q 128 95 128 77 L 128 45 Q 128 25 148 25 L 210 25 Q 230 25 230 45 L 230 65" fill="none" stroke="var(--accent)" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>
        <!-- Glowing Scales / Segments -->
        <circle cx="45" cy="95" r="3.2" fill="#FFF" opacity="0.6"/>
        <circle cx="75" cy="95" r="3.2" fill="#FFF" opacity="0.6"/>
        <circle cx="105" cy="95" r="3.2" fill="#FFF" opacity="0.6"/>
        <circle cx="128" cy="62" r="3.2" fill="#FFF" opacity="0.6"/>
        <circle cx="155" cy="25" r="3.2" fill="#FFF" opacity="0.6"/>
        <circle cx="185" cy="25" r="3.2" fill="#FFF" opacity="0.6"/>
        <!-- Snake Head with Eyes and Forked Tongue -->
        <g transform="translate(230, 68)">
          <rect x="-9" y="-8" width="18" height="20" rx="6" fill="var(--color-snow-white)"/>
          <circle cx="-4" cy="3" r="2.4" fill="#0F172A"/>
          <circle cx="4" cy="3" r="2.4" fill="#0F172A"/>
          <circle cx="-3.5" cy="2.5" r="0.9" fill="#FFF"/>
          <circle cx="4.5" cy="2.5" r="0.9" fill="#FFF"/>
          <path d="M 0 12 L 0 17 M -2.5 19.5 L 0 17 L 2.5 19.5" stroke="#FF4D4D" stroke-width="1.6" stroke-linecap="round"/>
        </g>
        <!-- Detailed Neon Apple with Stem, Leaf and Glow -->
        <g transform="translate(268, 88)">
          <circle cx="0" cy="0" r="16" fill="rgba(239,68,68,0.2)"/>
          <ellipse cx="0" cy="1" rx="10" ry="11" fill="#EF4444"/>
          <path d="M 0 -9 Q 3 -15 6 -14" fill="none" stroke="#A16207" stroke-width="2" stroke-linecap="round"/>
          <path d="M 2 -11 Q 7 -13 6 -8 Z" fill="#22C55E"/>
          <circle cx="-3.5" cy="-2.5" r="2.5" fill="rgba(255,255,255,0.45)"/>
        </g>
        <!-- Score Indicator -->
        <g transform="translate(24, 18)">
          <rect x="0" y="0" width="70" height="22" rx="6" fill="rgba(16,16,20,0.7)" stroke="rgba(255,255,255,0.1)"/>
          <text x="8" y="15" fill="#10B981" font-family="'DM Sans',sans-serif" font-weight="700" font-size="11">+15 PTS</text>
        </g>
      `;
    },

    // ------------------------------------------------------------------------
    // MINESWEEPER
    // ------------------------------------------------------------------------
    minesweeper: () => {
      // High-detail 3D contact mine + tactical grid tiles with numbers & flag
      return `
        <!-- Minefield Tile Grid -->
        <g opacity="0.35">
          <rect x="20" y="15" width="34" height="34" rx="4" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)"/>
          <rect x="58" y="15" width="34" height="34" rx="4" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)"/>
          <rect x="96" y="15" width="34" height="34" rx="4" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)"/>
          <rect x="20" y="53" width="34" height="34" rx="4" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)"/>
          <rect x="58" y="53" width="34" height="34" rx="4" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.15)"/>
          <rect x="96" y="53" width="34" height="34" rx="4" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)"/>
        </g>
        <!-- Exposed Indicator Numbers -->
        <text x="37" y="38" text-anchor="middle" fill="#3B82F6" font-family="'DM Sans',sans-serif" font-weight="800" font-size="20">1</text>
        <text x="75" y="38" text-anchor="middle" fill="#10B981" font-family="'DM Sans',sans-serif" font-weight="800" font-size="20">2</text>
        <text x="37" y="76" text-anchor="middle" fill="#EF4444" font-family="'DM Sans',sans-serif" font-weight="800" font-size="20">3</text>
        <!-- Triangular Red Flag on Tile -->
        <g transform="translate(96, 53)">
          <line x1="17" y1="8" x2="17" y2="28" stroke="#D1D5DB" stroke-width="2" stroke-linecap="round"/>
          <polygon points="17,8 6,14 17,20" fill="#EF4444"/>
          <rect x="12" y="27" width="10" height="3" rx="1.5" fill="#9CA3AF"/>
        </g>
        <!-- Realistic Spiked Naval Contact Mine -->
        <g transform="translate(230, 68)">
          <!-- Sonar Ripple Rings -->
          <circle cx="0" cy="0" r="50" fill="none" stroke="var(--accent)" stroke-width="1" stroke-dasharray="4 4" opacity="0.3"/>
          <circle cx="0" cy="0" r="42" fill="rgba(var(--accent-rgb),0.06)"/>
          <!-- 8 Spikes / Detonation Horns -->
          <line x1="0" y1="-32" x2="0" y2="32" stroke="var(--accent)" stroke-width="5" stroke-linecap="round"/>
          <line x1="-32" y1="0" x2="32" y2="0" stroke="var(--accent)" stroke-width="5" stroke-linecap="round"/>
          <line x1="-23" y1="-23" x2="23" y2="23" stroke="var(--accent)" stroke-width="5" stroke-linecap="round"/>
          <line x1="23" y1="-23" x2="-23" y2="23" stroke="var(--accent)" stroke-width="5" stroke-linecap="round"/>
          <!-- Spike Caps -->
          <circle cx="0" cy="-32" r="3.5" fill="var(--color-snow-white)"/>
          <circle cx="0" cy="32" r="3.5" fill="var(--color-snow-white)"/>
          <circle cx="-32" cy="0" r="3.5" fill="var(--color-snow-white)"/>
          <circle cx="32" cy="0" r="3.5" fill="var(--color-snow-white)"/>
          <circle cx="-23" cy="-23" r="3.5" fill="var(--color-snow-white)"/>
          <circle cx="23" cy="23" r="3.5" fill="var(--color-snow-white)"/>
          <circle cx="23" cy="-23" r="3.5" fill="var(--color-snow-white)"/>
          <circle cx="-23" cy="23" r="3.5" fill="var(--color-snow-white)"/>
          <!-- Mine Core Body -->
          <circle cx="0" cy="0" r="24" fill="#18181B" stroke="var(--accent)" stroke-width="2.5"/>
          <circle cx="0" cy="0" r="20" fill="rgba(var(--accent-rgb),0.25)"/>
          <!-- Flashing Red Danger LED -->
          <circle cx="0" cy="0" r="6" fill="#EF4444"/>
          <circle cx="0" cy="0" r="9" fill="none" stroke="#EF4444" stroke-width="1.5" opacity="0.6"/>
          <!-- Metallic Specular Arc -->
          <path d="M -14 -12 A 18 18 0 0 1 12 -14" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="2" stroke-linecap="round"/>
        </g>
      `;
    },

    // ------------------------------------------------------------------------
    // CHESS (4 Unique Detailed Mode Icons)
    // ------------------------------------------------------------------------
    chess: (i) => {
      if (i === 0) {
        // Mode 0: Blitz 3+2 - Isometric Chess Board, Digital Match Clock + Lightning Bolt + Charging Staunton Knight
        return `
          <defs>
            <radialGradient id="g_ch_0" cx="75%" cy="42%" r="55%">
              <stop offset="0%" stop-color="var(--accent)" stop-opacity="0.34"/>
              <stop offset="100%" stop-color="#09090B" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <rect width="320" height="180" fill="url(#g_ch_0)"/>
          <!-- Isometric Tournament Board Perspective -->
          <g transform="translate(-10, 20)" opacity="0.48">
            <polygon points="10,56 66,34 122,56 66,78" fill="rgba(255,255,255,0.06)" stroke="rgba(255,255,255,0.16)"/>
            <polygon points="66,34 122,12 178,34 122,56" fill="rgba(var(--accent-rgb),0.24)" stroke="rgba(255,255,255,0.16)"/>
            <polygon points="122,56 178,34 234,56 178,78" fill="rgba(255,255,255,0.06)" stroke="rgba(255,255,255,0.16)"/>
            <polygon points="66,78 122,56 178,78 122,100" fill="rgba(var(--accent-rgb),0.24)" stroke="rgba(255,255,255,0.16)"/>
            <polygon points="122,12 178,-10 234,12 178,34" fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.12)"/>
          </g>
          <!-- Dual Digital DGT-Style Chess Clock -->
          <g transform="translate(20, 18)">
            <rect x="2" y="4" width="122" height="44" rx="10" fill="rgba(0,0,0,0.55)"/>
            <rect x="0" y="0" width="122" height="44" rx="10" fill="#18181B" stroke="rgba(255,255,255,0.22)" stroke-width="1.5"/>
            <rect x="6" y="6" width="54" height="32" rx="6" fill="rgba(var(--accent-rgb),0.22)" stroke="var(--accent)" stroke-width="1.2"/>
            <text x="33" y="25" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="13">03:00</text>
            <text x="33" y="34" text-anchor="middle" fill="#F59E0B" font-family="'DM Sans',sans-serif" font-weight="800" font-size="7.5">+2 SEC</text>
            <rect x="64" y="6" width="52" height="32" rx="6" fill="rgba(255,255,255,0.06)"/>
            <text x="90" y="25" text-anchor="middle" fill="var(--color-ash)" font-family="'DM Sans',sans-serif" font-weight="800" font-size="13">02:54</text>
            <circle cx="109" cy="11" r="2.2" fill="#EF4444"/>
          </g>
          <!-- Speed Streaks & Electric Bolt -->
          <g stroke="#F59E0B" stroke-linecap="round" opacity="0.72">
            <line x1="154" y1="30" x2="210" y2="30" stroke-width="2" stroke-dasharray="16 6"/>
            <line x1="142" y1="48" x2="206" y2="48" stroke-width="2.5" stroke-dasharray="26 8"/>
            <line x1="164" y1="66" x2="214" y2="66" stroke-width="1.8" stroke-dasharray="12 6"/>
          </g>
          <polygon points="200,12 183,44 196,44 188,76 214,38 200,38" fill="#F59E0B" stroke="#FFF" stroke-width="1.2"/>
          <!-- Sculpted Staunton Tournament Knight -->
          <g transform="translate(216, 12)">
            <circle cx="48" cy="52" r="48" fill="rgba(var(--accent-rgb),0.14)" stroke="rgba(var(--accent-rgb),0.3)" stroke-dasharray="4 4"/>
            <ellipse cx="48" cy="96" rx="30" ry="7" fill="rgba(0,0,0,0.5)"/>
            <rect x="20" y="88" width="56" height="8" rx="3" fill="#27272A" stroke="rgba(255,255,255,0.28)" stroke-width="1"/>
            <rect x="24" y="81" width="48" height="7" rx="2" fill="#3F3F46"/>
            <path d="M 30 81 C 28 65 34 52 40 42 C 44 37 45 27 45 22 C 45 19 47 17 50 19 C 52 21 53 25 55 24 C 58 19 63 14 67 16 C 71 18 68 26 67 31 C 71 31 74 35 74 41 C 73 47 69 52 65 55 C 70 62 71 72 70 81 Z" fill="#18181B" stroke="var(--accent)" stroke-width="2.5" stroke-linejoin="round"/>
            <path d="M 63 22 C 58 27 56 34 57 41 M 56 34 C 52 40 50 47 51 55 M 50 48 C 46 55 45 64 46 74" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round"/>
            <circle cx="37" cy="46" r="2" fill="#F59E0B"/>
            <circle cx="49" cy="31" r="2.4" fill="#FFF"/>
            <path d="M 34 54 Q 41 59 48 54" fill="none" stroke="rgba(255,255,255,0.45)" stroke-width="1.8" stroke-linecap="round"/>
          </g>
        `;
      }
      if (i === 1) {
        // Mode 1: Rapid 5+0 - Regal Jeweled Staunton Queen + Tactical Target Crosshair + Analog-Digital Clock
        return `
          <defs>
            <radialGradient id="g_ch_1" cx="72%" cy="46%" r="52%">
              <stop offset="0%" stop-color="#F59E0B" stop-opacity="0.28"/>
              <stop offset="100%" stop-color="#09090B" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <rect width="320" height="180" fill="url(#g_ch_1)"/>
          <!-- Checkerboard Perspective Grid -->
          <g transform="translate(14, 14)" opacity="0.34">
            <rect x="0" y="0" width="32" height="32" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.12)"/>
            <rect x="32" y="0" width="32" height="32" fill="rgba(245,158,11,0.2)" stroke="rgba(255,255,255,0.12)"/>
            <rect x="64" y="0" width="32" height="32" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.12)"/>
            <rect x="0" y="32" width="32" height="32" fill="rgba(245,158,11,0.2)" stroke="rgba(255,255,255,0.12)"/>
            <rect x="32" y="32" width="32" height="32" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.12)"/>
            <rect x="64" y="32" width="32" height="32" fill="rgba(245,158,11,0.2)" stroke="rgba(255,255,255,0.12)"/>
          </g>
          <!-- Classical Twin Clock Showing 05:00 -->
          <g transform="translate(22, 56)">
            <rect x="2" y="4" width="124" height="44" rx="10" fill="rgba(0,0,0,0.55)"/>
            <rect x="0" y="0" width="124" height="44" rx="10" fill="#18181B" stroke="#F59E0B" stroke-width="1.4"/>
            <rect x="6" y="6" width="54" height="32" rx="6" fill="rgba(245,158,11,0.2)" stroke="#F59E0B" stroke-width="1"/>
            <text x="33" y="26" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="13">05:00</text>
            <rect x="64" y="6" width="54" height="32" rx="6" fill="rgba(255,255,255,0.06)"/>
            <text x="91" y="26" text-anchor="middle" fill="var(--color-ash)" font-family="'DM Sans',sans-serif" font-weight="800" font-size="13">05:00</text>
          </g>
          <!-- Tactical Targeting Reticle Rings -->
          <g transform="translate(242, 60)" stroke="rgba(245,158,11,0.42)" fill="none">
            <circle cx="0" cy="0" r="52" stroke-width="1.5" stroke-dasharray="7 5"/>
            <circle cx="0" cy="0" r="38" stroke-width="1"/>
            <line x1="-60" y1="0" x2="-44" y2="0" stroke-width="2"/>
            <line x1="44" y1="0" x2="60" y2="0" stroke-width="2"/>
          </g>
          <!-- Sculpted Imperial Staunton Queen -->
          <g transform="translate(202, 10)">
            <ellipse cx="40" cy="98" rx="28" ry="7" fill="rgba(0,0,0,0.55)"/>
            <rect x="14" y="88" width="52" height="8" rx="3" fill="#27272A" stroke="#F59E0B" stroke-width="1.3"/>
            <rect x="18" y="80" width="44" height="8" rx="2" fill="#3F3F46"/>
            <path d="M 22 80 C 22 64 26 48 25 38 L 55 38 C 54 48 58 64 58 80 Z" fill="#18181B" stroke="#F59E0B" stroke-width="2.4"/>
            <path d="M 24 38 L 12 18 L 26 29 L 40 8 L 54 29 L 68 18 L 56 38 Z" fill="#18181B" stroke="#F59E0B" stroke-width="2.4" stroke-linejoin="round"/>
            <circle cx="12" cy="17" r="3.5" fill="#F59E0B" stroke="#FFF" stroke-width="0.9"/>
            <circle cx="26" cy="27" r="2.5" fill="#F59E0B"/>
            <circle cx="40" cy="7" r="4.2" fill="#F59E0B" stroke="#FFF" stroke-width="1"/>
            <circle cx="54" cy="27" r="2.5" fill="#F59E0B"/>
            <circle cx="68" cy="17" r="3.5" fill="#F59E0B" stroke="#FFF" stroke-width="0.9"/>
            <ellipse cx="40" cy="39" rx="16" ry="3.5" fill="#F59E0B" opacity="0.65"/>
            <circle cx="40" cy="56" r="4.5" fill="var(--accent)" stroke="#FFF" stroke-width="1"/>
            <path d="M 29 45 C 29 58 30 68 28 76" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="2" stroke-linecap="round"/>
          </g>
        `;
      }
      if (i === 2) {
        // Mode 2: Host 2P Match - Grandmaster Duel: White Ivory King vs Black Obsidian King + Clash Spark
        return `
          <defs>
            <radialGradient id="g_ch_2" cx="50%" cy="50%" r="55%">
              <stop offset="0%" stop-color="var(--accent)" stop-opacity="0.22"/>
              <stop offset="100%" stop-color="#09090B" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <rect width="320" height="180" fill="url(#g_ch_2)"/>
          <!-- Split Duel Checkered Floor -->
          <polygon points="0,120 160,120 160,0 130,0" fill="rgba(255,255,255,0.03)"/>
          <polygon points="160,120 320,120 320,0 160,0" fill="rgba(var(--accent-rgb),0.08)"/>
          <line x1="160" y1="8" x2="160" y2="122" stroke="rgba(255,255,255,0.12)" stroke-dasharray="4 4"/>
          <!-- Ivory White King (Left Challenger) -->
          <g transform="translate(52, 16)">
            <ellipse cx="32" cy="92" rx="26" ry="6" fill="rgba(0,0,0,0.45)"/>
            <rect x="8" y="82" width="48" height="8" rx="3" fill="#D4D4D8" stroke="#18181B" stroke-width="1.2"/>
            <rect x="12" y="75" width="40" height="7" rx="2" fill="#E4E4E7"/>
            <path d="M 15 75 L 20 40 L 44 40 L 49 75 Z" fill="#FAFAFA" stroke="#18181B" stroke-width="2.2"/>
            <path d="M 15 40 L 11 24 L 32 31 L 53 24 L 49 40 Z" fill="#FAFAFA" stroke="#18181B" stroke-width="2.2" stroke-linejoin="round"/>
            <line x1="32" y1="6" x2="32" y2="27" stroke="#FAFAFA" stroke-width="4.5" stroke-linecap="round"/>
            <line x1="23" y1="14" x2="41" y2="14" stroke="#FAFAFA" stroke-width="4.5" stroke-linecap="round"/>
            <ellipse cx="32" cy="41" rx="14" ry="3" fill="#18181B" opacity="0.2"/>
          </g>
          <!-- Crossed Steel Sabers & Impact Flash -->
          <g transform="translate(160, 56)">
            <circle cx="0" cy="0" r="24" fill="rgba(245,158,11,0.16)"/>
            <line x1="-26" y1="-22" x2="26" y2="22" stroke="#E4E4E7" stroke-width="3.8" stroke-linecap="round"/>
            <line x1="26" y1="-22" x2="-26" y2="22" stroke="#F59E0B" stroke-width="3.8" stroke-linecap="round"/>
            <polygon points="0,-10 3,-3 10,0 3,3 0,10 -3,3 -10,0 -3,-3" fill="var(--accent)" stroke="#FFF" stroke-width="1"/>
          </g>
          <!-- Obsidian & Crimson King (Right Rival) -->
          <g transform="translate(204, 16)">
            <ellipse cx="32" cy="92" rx="26" ry="6" fill="rgba(0,0,0,0.55)"/>
            <rect x="8" y="82" width="48" height="8" rx="3" fill="#27272A" stroke="var(--accent)" stroke-width="1.2"/>
            <rect x="12" y="75" width="40" height="7" rx="2" fill="#3F3F46"/>
            <path d="M 15 75 L 20 40 L 44 40 L 49 75 Z" fill="#18181B" stroke="var(--accent)" stroke-width="2.2"/>
            <path d="M 15 40 L 11 24 L 32 31 L 53 24 L 49 40 Z" fill="#18181B" stroke="var(--accent)" stroke-width="2.2" stroke-linejoin="round"/>
            <line x1="32" y1="6" x2="32" y2="27" stroke="var(--accent)" stroke-width="4.5" stroke-linecap="round"/>
            <line x1="23" y1="14" x2="41" y2="14" stroke="var(--accent)" stroke-width="4.5" stroke-linecap="round"/>
            <ellipse cx="32" cy="41" rx="14" ry="3" fill="var(--accent)" opacity="0.35"/>
          </g>
        `;
      }
      // Mode 3: Custom Chess Board - Full Illuminated Architectural Blueprint + Palette Pieces + Target Placement
      return `
        <defs>
          <pattern id="g_ch_3_grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <rect width="20" height="20" fill="none" stroke="rgba(56,189,248,0.16)" stroke-width="1"/>
          </pattern>
        </defs>
        <rect width="320" height="180" fill="url(#g_ch_3_grid)"/>
        <!-- Left Piece Selection Palette Tray -->
        <g transform="translate(20, 18)">
          <rect x="0" y="0" width="94" height="90" rx="10" fill="rgba(16,16,22,0.88)" stroke="rgba(56,189,248,0.45)" stroke-width="1.5"/>
          <rect x="7" y="7" width="38" height="36" rx="6" fill="rgba(56,189,248,0.22)" stroke="#38BDF8" stroke-width="1.4"/>
          <text x="26" y="33" text-anchor="middle" fill="#FFF" font-size="24">♔</text>
          <rect x="49" y="7" width="38" height="36" rx="6" fill="rgba(255,255,255,0.06)"/>
          <text x="68" y="33" text-anchor="middle" fill="#E4E4E7" font-size="24">♕</text>
          <rect x="7" y="47" width="38" height="36" rx="6" fill="rgba(255,255,255,0.06)"/>
          <text x="26" y="73" text-anchor="middle" fill="var(--accent)" font-size="24">♜</text>
          <rect x="49" y="47" width="38" height="36" rx="6" fill="rgba(255,255,255,0.06)"/>
          <text x="68" y="73" text-anchor="middle" fill="#F59E0B" font-size="24">♞</text>
        </g>
        <!-- Dragging Curve from Tray to Board -->
        <path d="M 114 34 Q 148 14 176 34" fill="none" stroke="#38BDF8" stroke-width="2" stroke-dasharray="4 3"/>
        <!-- Interactive 3x3 Custom Blueprint Sub-Board -->
        <g transform="translate(174, 14)">
          <rect x="2" y="4" width="114" height="98" rx="10" fill="rgba(0,0,0,0.55)"/>
          <rect x="0" y="0" width="114" height="98" rx="10" fill="#18181B" stroke="#38BDF8" stroke-width="2"/>
          <rect x="6" y="6" width="32" height="28" rx="3" fill="#D4D4D8" opacity="0.22"/>
          <rect x="41" y="6" width="32" height="28" rx="3" fill="rgba(56,189,248,0.28)" stroke="#38BDF8" stroke-width="1.5"/>
          <rect x="76" y="6" width="32" height="28" rx="3" fill="#D4D4D8" opacity="0.22"/>
          <rect x="6" y="36" width="32" height="28" rx="3" fill="rgba(255,255,255,0.05)"/>
          <rect x="41" y="36" width="32" height="28" rx="3" fill="#D4D4D8" opacity="0.22"/>
          <rect x="76" y="36" width="32" height="28" rx="3" fill="rgba(255,255,255,0.05)"/>
          <rect x="6" y="66" width="32" height="26" rx="3" fill="#D4D4D8" opacity="0.22"/>
          <rect x="41" y="66" width="32" height="26" rx="3" fill="rgba(255,255,255,0.05)"/>
          <rect x="76" y="66" width="32" height="26" rx="3" fill="#D4D4D8" opacity="0.22"/>
          <!-- Placed Pieces -->
          <text x="57" y="28" text-anchor="middle" fill="#FFF" font-size="22">♔</text>
          <text x="22" y="86" text-anchor="middle" fill="var(--accent)" font-size="21">♛</text>
          <!-- Active Cursor Crosshair on d4 -->
          <circle cx="92" cy="50" r="11" fill="none" stroke="#F59E0B" stroke-width="1.8" stroke-dasharray="3 2"/>
          <line x1="92" y1="36" x2="92" y2="64" stroke="#F59E0B" stroke-width="1.2"/>
          <line x1="78" y1="50" x2="106" y2="50" stroke="#F59E0B" stroke-width="1.2"/>
        </g>
      `;
    },

    // ------------------------------------------------------------------------
    // UNO (3 Unique Detailed Mode Icons)
    // ------------------------------------------------------------------------
    uno: (i) => {
      if (i === 0) {
        // 1v1 UNO Duel: Diagonal Cobalt +2 Draw Attack vs Crimson Reverse Cards + Energy Clash
        return `
          <defs>
            <radialGradient id="g_uno_0" cx="55%" cy="50%" r="55%">
              <stop offset="0%" stop-color="#EF4444" stop-opacity="0.25"/>
              <stop offset="100%" stop-color="#09090B" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <rect width="320" height="180" fill="url(#g_uno_0)"/>
          <!-- Diagonal Attack Bolt Streaks -->
          <line x1="20" y1="95" x2="115" y2="35" stroke="#3B82F6" stroke-width="3" stroke-dasharray="10 6" opacity="0.5"/>
          <line x1="205" y1="95" x2="295" y2="25" stroke="#EF4444" stroke-width="3" stroke-dasharray="10 6" opacity="0.5"/>
          <!-- Left Attacking Blue +2 Card -->
          <g transform="translate(54, 16) rotate(-14 35 50)">
            <rect x="4" y="5" width="68" height="98" rx="11" fill="rgba(0,0,0,0.5)"/>
            <rect x="0" y="0" width="68" height="98" rx="11" fill="#2563EB" stroke="#FFF" stroke-width="2.2"/>
            <ellipse cx="34" cy="49" rx="24" ry="37" fill="#FFF" opacity="0.95" transform="rotate(24 34 49)"/>
            <text x="34" y="58" text-anchor="middle" fill="#2563EB" font-family="'DM Sans',sans-serif" font-weight="900" font-size="28">+2</text>
            <text x="8" y="16" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="800" font-size="10">+2</text>
          </g>
          <!-- Center Clash VS Spark -->
          <g transform="translate(158, 56)">
            <circle cx="0" cy="0" r="18" fill="#18181B" stroke="#F59E0B" stroke-width="2"/>
            <text x="0" y="5" text-anchor="middle" fill="#F59E0B" font-family="'DM Sans',sans-serif" font-weight="900" font-size="13">1v1</text>
          </g>
          <!-- Right Countering Red Reverse Card -->
          <g transform="translate(194, 14) rotate(12 35 50)">
            <rect x="4" y="5" width="68" height="98" rx="11" fill="rgba(0,0,0,0.5)"/>
            <rect x="0" y="0" width="68" height="98" rx="11" fill="#EF4444" stroke="#FFF" stroke-width="2.4"/>
            <ellipse cx="34" cy="49" rx="24" ry="37" fill="#FFF" opacity="0.95" transform="rotate(24 34 49)"/>
            <text x="34" y="61" text-anchor="middle" fill="#EF4444" font-family="'DM Sans',sans-serif" font-weight="900" font-size="38">⇄</text>
            <text x="8" y="16" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="800" font-size="11">⇄</text>
          </g>
        `;
      }
      if (i === 1) {
        // 4-Player Table: Seamless 4-Color Orbital Ring Connecting 4 Seat Tokens & Wild +4 Hero
        return `
          <defs>
            <radialGradient id="g_uno_1" cx="55%" cy="52%" r="55%">
              <stop offset="0%" stop-color="#10B981" stop-opacity="0.22"/>
              <stop offset="100%" stop-color="#09090B" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <rect width="320" height="180" fill="url(#g_uno_1)"/>
          <!-- 4-Quadrant Turn Orbit -->
          <g transform="translate(160, 62)">
            <circle cx="0" cy="0" r="56" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8"/>
            <path d="M 0 -56 A 56 56 0 0 1 56 0" fill="none" stroke="#EF4444" stroke-width="7" stroke-linecap="round"/>
            <path d="M 56 0 A 56 56 0 0 1 0 56" fill="none" stroke="#3B82F6" stroke-width="7" stroke-linecap="round"/>
            <path d="M 0 56 A 56 56 0 0 1 -56 0" fill="none" stroke="#EAB308" stroke-width="7" stroke-linecap="round"/>
            <path d="M -56 0 A 56 56 0 0 1 0 -56" fill="none" stroke="#10B981" stroke-width="7" stroke-linecap="round"/>
            <!-- Seat Indicator Pips -->
            <circle cx="-64" cy="0" r="8" fill="#10B981" stroke="#FFF" stroke-width="1.5"/>
            <circle cx="64" cy="0" r="8" fill="#3B82F6" stroke="#FFF" stroke-width="1.5"/>
          </g>
          <!-- Center Obsidian Wild +4 Hero Card -->
          <g transform="translate(126, 12)">
            <rect x="4" y="5" width="68" height="100" rx="11" fill="rgba(0,0,0,0.55)"/>
            <rect x="0" y="0" width="68" height="100" rx="11" fill="#18181B" stroke="#FFF" stroke-width="2.4"/>
            <ellipse cx="34" cy="50" rx="25" ry="38" fill="#000" transform="rotate(22 34 50)"/>
            <g transform="translate(34, 50) rotate(22)">
              <rect x="-13" y="-19" width="12" height="18" rx="3" fill="#EF4444" stroke="#FFF" stroke-width="0.6"/>
              <rect x="1" y="-19" width="12" height="18" rx="3" fill="#3B82F6" stroke="#FFF" stroke-width="0.6"/>
              <rect x="-13" y="1" width="12" height="18" rx="3" fill="#EAB308" stroke="#FFF" stroke-width="0.6"/>
              <rect x="1" y="1" width="12" height="18" rx="3" fill="#10B981" stroke="#FFF" stroke-width="0.6"/>
            </g>
            <text x="8" y="17" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="12">+4</text>
          </g>
        `;
      }
      // Mode 2: Host 2-6P Party - Rich Rainbow Card Fan (Green 9, Yellow Skip, Wild +4) + Ribbon
      return `
        <circle cx="170" cy="64" r="68" fill="rgba(245,158,11,0.14)"/>
        <g transform="translate(66, 20) rotate(-24 30 45)">
          <rect x="0" y="0" width="58" height="86" rx="10" fill="#10B981" stroke="#FFF" stroke-width="2"/>
          <ellipse cx="29" cy="43" rx="20" ry="32" fill="#FFF" opacity="0.92" transform="rotate(24 29 43)"/>
          <text x="29" y="54" text-anchor="middle" fill="#10B981" font-family="'DM Sans',sans-serif" font-weight="900" font-size="30">9</text>
        </g>
        <g transform="translate(114, 12) rotate(-8 30 45)">
          <rect x="0" y="0" width="58" height="86" rx="10" fill="#EAB308" stroke="#FFF" stroke-width="2"/>
          <ellipse cx="29" cy="43" rx="20" ry="32" fill="#FFF" opacity="0.92" transform="rotate(24 29 43)"/>
          <text x="29" y="54" text-anchor="middle" fill="#CA8A04" font-family="'DM Sans',sans-serif" font-weight="900" font-size="30">⊘</text>
        </g>
        <g transform="translate(160, 12) rotate(8 30 45)">
          <rect x="0" y="0" width="58" height="86" rx="10" fill="#3B82F6" stroke="#FFF" stroke-width="2"/>
          <ellipse cx="29" cy="43" rx="20" ry="32" fill="#FFF" opacity="0.92" transform="rotate(24 29 43)"/>
          <text x="29" y="52" text-anchor="middle" fill="#2563EB" font-family="'DM Sans',sans-serif" font-weight="900" font-size="24">+2</text>
        </g>
        <g transform="translate(206, 20) rotate(24 30 45)">
          <rect x="0" y="0" width="60" height="88" rx="10" fill="#18181B" stroke="#FFF" stroke-width="2.4"/>
          <g transform="translate(30, 44) rotate(22)">
            <rect x="-12" y="-17" width="11" height="16" rx="2.5" fill="#EF4444"/>
            <rect x="1" y="-17" width="11" height="16" rx="2.5" fill="#3B82F6"/>
            <rect x="-12" y="1" width="11" height="16" rx="2.5" fill="#EAB308"/>
            <rect x="1" y="1" width="11" height="16" rx="2.5" fill="#10B981"/>
          </g>
          <text x="8" y="17" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="800" font-size="11">+4</text>
        </g>
        <!-- UNO Shout Gold-Stitched Emblem -->
        <g transform="translate(120, 74) rotate(-5)">
          <rect x="0" y="0" width="84" height="30" rx="14" fill="var(--accent)" stroke="#FFF" stroke-width="2"/>
          <text x="42" y="21" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="15" letter-spacing="2">UNO!</text>
        </g>
      `;
    },

    // ------------------------------------------------------------------------
    // MONOPOLY (3 Unique Detailed Mode Icons)
    // ------------------------------------------------------------------------
    monopoly: (i) => {
      if (i === 0) {
        // 1v1 Economy Duel: Fanned Emerald & Crimson Cash Notes + Dark Blue Boardwalk Deed + Top Hat Token
        return `
          <g transform="translate(26, 20) rotate(-14)">
            <rect x="0" y="0" width="88" height="48" rx="6" fill="#047857" stroke="#34D399" stroke-width="2"/>
            <circle cx="44" cy="24" r="14" fill="rgba(255,255,255,0.18)"/>
            <text x="44" y="29" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="15">$100</text>
          </g>
          <g transform="translate(36, 48) rotate(-4)">
            <rect x="0" y="0" width="90" height="48" rx="6" fill="#B45309" stroke="#FDE047" stroke-width="2"/>
            <circle cx="45" cy="24" r="14" fill="rgba(255,255,255,0.18)"/>
            <text x="45" y="29" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="15">$500</text>
          </g>
          <!-- Sculpted Dark-Blue Boardwalk Title Deed -->
          <g transform="translate(152, 14) rotate(5)">
            <rect x="4" y="5" width="72" height="94" rx="8" fill="rgba(0,0,0,0.5)"/>
            <rect x="0" y="0" width="72" height="94" rx="8" fill="#FFF" stroke="#27272A" stroke-width="2"/>
            <rect x="5" y="5" width="62" height="25" rx="4" fill="#1D4ED8"/>
            <text x="36" y="21" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="8.5" letter-spacing="0.5">BOARDWALK</text>
            <line x1="12" y1="42" x2="60" y2="42" stroke="#9CA3AF" stroke-width="1.5"/>
            <line x1="12" y1="53" x2="60" y2="53" stroke="#9CA3AF" stroke-width="1.5"/>
            <line x1="12" y1="64" x2="60" y2="64" stroke="#9CA3AF" stroke-width="1.5"/>
            <text x="36" y="83" text-anchor="middle" fill="#111827" font-family="'DM Sans',sans-serif" font-weight="900" font-size="13">$400</text>
          </g>
          <!-- Metallic Top Hat Piece -->
          <g transform="translate(248, 36)">
            <ellipse cx="22" cy="52" rx="22" ry="7" fill="#D4D4D8" stroke="#18181B" stroke-width="1.5"/>
            <path d="M 8 50 L 11 16 L 33 16 L 36 50 Z" fill="#E4E4E7" stroke="#18181B" stroke-width="1.5"/>
            <rect x="9.5" y="39" width="25" height="7" fill="var(--accent)"/>
          </g>
        `;
      }
      if (i === 1) {
        // 4P Tycoon: Isometric Real-Estate Skyline (3 Houses + Grand Hotel) + Live Auction Gavel
        return `
          <!-- Isometric Property Track Strip -->
          <g transform="translate(28, 60)" opacity="0.5">
            <polygon points="0,30 140,0 260,30 120,60" fill="rgba(16,185,129,0.12)" stroke="rgba(255,255,255,0.2)"/>
          </g>
          <!-- Emerald Houses & Crimson Hotel Cluster -->
          <g transform="translate(46, 28)">
            <polygon points="8,44 24,26 40,44" fill="#059669" stroke="#064E3B"/>
            <rect x="8" y="44" width="32" height="28" fill="#10B981" stroke="#064E3B" stroke-width="1.2"/>
            <polygon points="48,44 64,26 80,44" fill="#059669" stroke="#064E3B"/>
            <rect x="48" y="44" width="32" height="28" fill="#10B981" stroke="#064E3B" stroke-width="1.2"/>
            <polygon points="90,26 116,4 142,26" fill="#991B1B" stroke="#450A0A"/>
            <rect x="90" y="26" width="52" height="46" fill="#EF4444" stroke="#7F1D1D" stroke-width="1.5"/>
            <rect x="125" y="10" width="7" height="16" fill="#B91C1C"/>
            <rect x="108" y="44" width="14" height="28" fill="#FEF08A" opacity="0.6"/>
          </g>
          <!-- Wooden Auction Gavel & Timer Ring -->
          <g transform="translate(232, 46)">
            <circle cx="0" cy="0" r="38" fill="rgba(245,158,11,0.14)" stroke="#F59E0B" stroke-width="1.8" stroke-dasharray="6 4"/>
            <g transform="rotate(32)">
              <rect x="-18" y="-22" width="36" height="18" rx="4" fill="#B45309" stroke="#FDE68A" stroke-width="1.5"/>
              <rect x="-4" y="-4" width="8" height="34" rx="3" fill="#92400E" stroke="#FDE68A" stroke-width="0.8"/>
            </g>
            <ellipse cx="0" cy="24" rx="22" ry="6" fill="#27272A" stroke="#F59E0B" stroke-width="1.4"/>
          </g>
        `;
      }
      // Host 2-6P: Full Corner GO Board Square + Rolling Casino Dice + $200 Salary Seal
      return `
        <g transform="translate(46, 16)">
          <rect x="4" y="4" width="128" height="94" rx="12" fill="rgba(0,0,0,0.55)"/>
          <rect x="0" y="0" width="128" height="94" rx="12" fill="#18181B" stroke="rgba(255,255,255,0.28)" stroke-width="2"/>
          <text x="64" y="42" text-anchor="middle" fill="#EF4444" font-family="'DM Sans',sans-serif" font-weight="900" font-size="34">GO</text>
          <path d="M 26 64 L 96 64 L 84 52 M 96 64 L 84 76" fill="none" stroke="#EF4444" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
          <text x="64" y="85" text-anchor="middle" fill="#10B981" font-family="'DM Sans',sans-serif" font-weight="800" font-size="10">COLLECT $200</text>
        </g>
        <!-- Pair of Precision Casino Dice -->
        <g transform="translate(200, 26) rotate(-10)">
          <rect x="3" y="4" width="38" height="38" rx="8" fill="rgba(0,0,0,0.45)"/>
          <rect x="0" y="0" width="38" height="38" rx="8" fill="#FFF" stroke="#D4D4D8" stroke-width="2"/>
          <circle cx="11" cy="11" r="3" fill="#18181B"/><circle cx="27" cy="11" r="3" fill="#18181B"/>
          <circle cx="19" cy="19" r="3.4" fill="#EF4444"/>
          <circle cx="11" cy="27" r="3" fill="#18181B"/><circle cx="27" cy="27" r="3" fill="#18181B"/>
        </g>
        <g transform="translate(238, 52) rotate(16)">
          <rect x="3" y="4" width="38" height="38" rx="8" fill="rgba(0,0,0,0.45)"/>
          <rect x="0" y="0" width="38" height="38" rx="8" fill="#FFF" stroke="#D4D4D8" stroke-width="2"/>
          <circle cx="11" cy="11" r="3" fill="#18181B"/><circle cx="19" cy="19" r="3" fill="#18181B"/><circle cx="27" cy="27" r="3" fill="#18181B"/>
        </g>
      `;
    },

    // ------------------------------------------------------------------------
    // GLOBE PROTOCOL (6 Unique Detailed Mode Icons)
    // ------------------------------------------------------------------------
    globe: (i) => {
      if (i === 1) {
        // Mode 1: Locate by Name - Radar Ping Sonar Waves Locking Continent Coordinate
        return `
          <defs>
            <radialGradient id="g_glb_1" cx="62%" cy="50%" r="55%">
              <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.28"/>
              <stop offset="100%" stop-color="#090D16" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <rect width="320" height="180" fill="url(#g_glb_1)"/>
          <!-- Continent Topographic Silhouette -->
          <path d="M 48 68 Q 70 28 115 38 Q 145 50 132 88 Q 100 105 64 90 Z" fill="rgba(56,189,248,0.2)" stroke="#38BDF8" stroke-width="1.5"/>
          <path d="M 185 32 Q 230 15 268 42 Q 288 74 242 98 Q 198 85 185 32 Z" fill="rgba(var(--accent-rgb),0.25)" stroke="var(--accent)" stroke-width="1.8"/>
          <!-- Active Sonar Crosshair -->
          <g transform="translate(230, 56)">
            <circle cx="0" cy="0" r="46" fill="none" stroke="#38BDF8" stroke-width="1.4" stroke-dasharray="5 4"/>
            <circle cx="0" cy="0" r="28" fill="none" stroke="#38BDF8" stroke-width="1.6"/>
            <line x1="-54" y1="0" x2="54" y2="0" stroke="rgba(56,189,248,0.4)" stroke-width="1.2"/>
            <line x1="0" y1="-54" x2="0" y2="54" stroke="rgba(56,189,248,0.4)" stroke-width="1.2"/>
            <circle cx="0" cy="0" r="6" fill="var(--accent)" stroke="#FFF" stroke-width="1.5"/>
          </g>
        `;
      }
      if (i === 2) {
        // Mode 2: Flag Pinpoint - Illuminated National Flag Banner on Globe Rim
        return `
          <g transform="translate(150, 12)">
            <circle cx="20" cy="110" r="76" fill="rgba(var(--accent-rgb),0.12)" stroke="rgba(255,255,255,0.22)" stroke-width="1.5"/>
            <ellipse cx="20" cy="110" rx="76" ry="24" fill="none" stroke="rgba(255,255,255,0.14)" stroke-dasharray="4 4"/>
          </g>
          <g transform="translate(134, 14)">
            <ellipse cx="36" cy="84" rx="22" ry="7" fill="rgba(var(--accent-rgb),0.3)" stroke="var(--accent)" stroke-width="1.5"/>
            <line x1="36" y1="10" x2="36" y2="84" stroke="#FAFAFA" stroke-width="3.5" stroke-linecap="round"/>
            <circle cx="36" cy="10" r="3" fill="#F59E0B"/>
            <path d="M 38 14 Q 68 6 98 20 L 98 54 Q 68 40 38 48 Z" fill="var(--accent)" stroke="#FFF" stroke-width="1.6"/>
            <polygon points="68,23 71,30 78,30 72,34 74,41 68,37 62,41 64,34 58,30 65,30" fill="#FFF"/>
          </g>
        `;
      }
      if (i === 3) {
        // Mode 3: Hint Detective - Illuminated Magnifying Lens Over Terrain Contours
        return `
          <g transform="translate(40, 20)" opacity="0.4">
            <ellipse cx="120" cy="45" rx="90" ry="38" fill="none" stroke="#10B981" stroke-width="1.2" stroke-dasharray="6 4"/>
            <ellipse cx="120" cy="45" rx="64" ry="26" fill="none" stroke="#10B981" stroke-width="1.2"/>
          </g>
          <g transform="translate(154, 52)">
            <circle cx="0" cy="0" r="42" fill="rgba(16,185,129,0.14)" stroke="#10B981" stroke-width="5"/>
            <path d="M -22 6 Q -8 -18 16 -8 Q 24 6 8 24 Z" fill="#10B981" opacity="0.5"/>
            <line x1="29" y1="29" x2="56" y2="56" stroke="#E4E4E7" stroke-width="9" stroke-linecap="round"/>
            <path d="M -24 -22 A 34 34 0 0 1 20 -26" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="2" stroke-linecap="round"/>
            <text x="0" y="9" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="24">?</text>
          </g>
        `;
      }
      if (i === 4) {
        // Mode 4: Border Bridge - Glowing Great-Circle Hop Arc Between Two Nation Polygons
        return `
          <g transform="translate(46, 18)">
            <polygon points="6,46 40,18 68,48 34,76" fill="rgba(56,189,248,0.32)" stroke="#38BDF8" stroke-width="2.2"/>
            <polygon points="154,28 198,14 214,56 168,72" fill="rgba(239,68,68,0.32)" stroke="#EF4444" stroke-width="2.2"/>
            <path d="M 38 46 Q 112 -6 184 42" fill="none" stroke="#F59E0B" stroke-width="3.5" stroke-dasharray="7 4"/>
            <circle cx="38" cy="46" r="6" fill="#38BDF8" stroke="#FFF" stroke-width="1.8"/>
            <circle cx="88" cy="19" r="5" fill="#F59E0B" stroke="#FFF" stroke-width="1.5"/>
            <circle cx="136" cy="20" r="5" fill="#F59E0B" stroke="#FFF" stroke-width="1.5"/>
            <circle cx="184" cy="42" r="6" fill="#EF4444" stroke="#FFF" stroke-width="1.8"/>
          </g>
        `;
      }
      if (i === 5) {
        // Mode 5: Host 16P Globe Race - Multi-node Broadcast Orbit Around Dark Earth
        return `
          <g transform="translate(160, 60)">
            <circle cx="0" cy="0" r="50" fill="#090D16" stroke="var(--accent)" stroke-width="2"/>
            <ellipse cx="0" cy="0" rx="50" ry="16" fill="none" stroke="rgba(255,255,255,0.22)"/>
            <ellipse cx="0" cy="0" rx="22" ry="50" fill="none" stroke="rgba(255,255,255,0.22)"/>
            <ellipse cx="0" cy="0" rx="68" ry="24" fill="none" stroke="var(--accent)" stroke-width="1.4" stroke-dasharray="5 4" transform="rotate(-18)"/>
            <circle cx="-32" cy="-16" r="6" fill="#38BDF8" stroke="#FFF" stroke-width="1.5"/>
            <circle cx="30" cy="-12" r="6" fill="#10B981" stroke="#FFF" stroke-width="1.5"/>
            <circle cx="4" cy="28" r="6" fill="#F59E0B" stroke="#FFF" stroke-width="1.5"/>
          </g>
        `;
      }
      // Mode 0: All 4 Modes Mix - Wireframe Globe + Brass Compass Rose
      return `
        <g transform="translate(216, 60)">
          <circle cx="0" cy="0" r="52" fill="rgba(var(--accent-rgb),0.1)"/>
          <circle cx="0" cy="0" r="48" fill="#090D16" stroke="var(--accent)" stroke-width="2"/>
          <ellipse cx="0" cy="0" rx="48" ry="16" fill="none" stroke="rgba(255,255,255,0.22)" stroke-dasharray="3 3"/>
          <ellipse cx="0" cy="0" rx="20" ry="48" fill="none" stroke="rgba(255,255,255,0.25)"/>
          <path d="M -26 12 Q 0 -30 28 8" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round"/>
          <circle cx="-26" cy="12" r="4" fill="var(--accent)"/><circle cx="28" cy="8" r="4" fill="#38BDF8"/>
        </g>
        <g transform="translate(74, 58)">
          <circle cx="0" cy="0" r="34" fill="none" stroke="rgba(var(--accent-rgb),0.35)" stroke-dasharray="3 3"/>
          <polygon points="0,-28 5,-7 24,0 5,7 0,28 -5,7 -24,0 -5,-7" fill="var(--accent)" opacity="0.72"/>
          <circle cx="0" cy="0" r="3.5" fill="#FFF"/>
          <text x="0" y="-32" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="800" font-size="9">N</text>
        </g>
      `;
    },

    // ------------------------------------------------------------------------
    // QA TRIVIA & ATLAS (7 Unique Detailed Mode Icons)
    // ------------------------------------------------------------------------
    qa_trivia: (i) => {
      if (i === 0) {
        // War topic: Crossed Officer Sabers + Shield Emblem over Radar Reticle
        return `
          <circle cx="160" cy="60" r="54" fill="none" stroke="rgba(239,68,68,0.28)" stroke-width="1.4"/>
          <circle cx="160" cy="60" r="38" fill="rgba(239,68,68,0.08)" stroke="rgba(239,68,68,0.45)" stroke-dasharray="5 3"/>
          <g transform="translate(160, 60)">
            <line x1="-38" y1="-34" x2="38" y2="34" stroke="#E4E4E7" stroke-width="4" stroke-linecap="round"/>
            <line x1="24" y1="22" x2="32" y2="14" stroke="#F59E0B" stroke-width="3.2" stroke-linecap="round"/>
            <line x1="38" y1="-34" x2="-38" y2="34" stroke="#E4E4E7" stroke-width="4" stroke-linecap="round"/>
            <line x1="-24" y1="22" x2="-32" y2="14" stroke="#F59E0B" stroke-width="3.2" stroke-linecap="round"/>
            <polygon points="0,-16 14,-6 11,11 0,18 -11,11 -14,-6" fill="#B91C1C" stroke="#FFF" stroke-width="1.8"/>
            <polygon points="0,-6 2,-2 6,-2 3,1 4,6 0,3 -4,6 -3,1 -6,-2 -2,-2" fill="#FFF"/>
          </g>
        `;
      }
      if (i === 2) {
        // World Atlas: Meridian Sphere + Brass Compass Star
        return `
          <g transform="translate(160, 60)">
            <circle cx="0" cy="0" r="48" fill="#090D16" stroke="#10B981" stroke-width="2.2"/>
            <ellipse cx="0" cy="0" rx="48" ry="16" fill="none" stroke="rgba(16,185,129,0.4)"/>
            <ellipse cx="0" cy="0" rx="20" ry="48" fill="none" stroke="rgba(16,185,129,0.4)"/>
            <polygon points="0,-28 7,-7 28,0 7,7 0,28 -7,7 -28,0 -7,-7" fill="#F59E0B" stroke="#FFF" stroke-width="1"/>
            <circle cx="0" cy="0" r="4" fill="#FFF"/>
          </g>
        `;
      }
      if (i === 3) {
        // Flags: Waving Fanned Multi-Nation Ribbon Banners
        return `
          <g transform="translate(58, 26) rotate(-10)">
            <rect x="0" y="0" width="64" height="40" rx="5" fill="#EF4444" stroke="#FFF" stroke-width="1.8"/>
            <rect x="0" y="14" width="64" height="12" fill="#FFF"/>
          </g>
          <g transform="translate(126, 18)">
            <rect x="0" y="0" width="68" height="44" rx="5" fill="#2563EB" stroke="#FFF" stroke-width="2"/>
            <circle cx="34" cy="22" r="11" fill="#F59E0B"/>
          </g>
          <g transform="translate(196, 26) rotate(10)">
            <rect x="0" y="0" width="64" height="40" rx="5" fill="#10B981" stroke="#FFF" stroke-width="1.8"/>
            <polygon points="0,0 28,20 0,40" fill="#EAB308"/>
          </g>
        `;
      }
      if (i === 4) {
        // Logic & Pattern IQ: Glowing Isometric 3D Rubik/Pattern Cube
        return `
          <g transform="translate(160, 58)">
            <circle cx="0" cy="0" r="52" fill="rgba(168,85,247,0.14)"/>
            <polygon points="0,-44 40,-22 0,0 -40,-22" fill="#A855F7" stroke="#FFF" stroke-width="1.6"/>
            <polygon points="-40,-22 0,0 0,44 -40,22" fill="#7E22CE" stroke="#FFF" stroke-width="1.6"/>
            <polygon points="40,-22 40,22 0,44 0,0" fill="#581C87" stroke="#FFF" stroke-width="1.6"/>
            <text x="0" y="-15" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="16">IQ</text>
          </g>
        `;
      }
      if (i === 5) {
        // Science Sprint: Orbiting Bohr Atom Model with Nucleons
        return `
          <g transform="translate(160, 60)">
            <ellipse cx="0" cy="0" rx="52" ry="18" fill="none" stroke="#38BDF8" stroke-width="2.2" transform="rotate(30)"/>
            <ellipse cx="0" cy="0" rx="52" ry="18" fill="none" stroke="#10B981" stroke-width="2.2" transform="rotate(-30)"/>
            <ellipse cx="0" cy="0" rx="52" ry="18" fill="none" stroke="#F59E0B" stroke-width="2.2" transform="rotate(90)"/>
            <circle cx="0" cy="0" r="10" fill="#EF4444" stroke="#FFF" stroke-width="1.8"/>
            <circle cx="44" cy="-14" r="4" fill="#FFF"/>
            <circle cx="-40" cy="22" r="4" fill="#38BDF8"/>
          </g>
        `;
      }
      if (i === 6) {
        // Host 16P Showdown: Podium Championship Trophy + Live Beacon
        return `
          <g transform="translate(106, 26)">
            <rect x="0" y="34" width="32" height="42" rx="5" fill="#3F3F46" stroke="rgba(255,255,255,0.2)"/>
            <rect x="38" y="10" width="36" height="66" rx="5" fill="var(--accent)" stroke="#FFF" stroke-width="1.5"/>
            <rect x="80" y="42" width="32" height="34" rx="5" fill="#27272A" stroke="rgba(255,255,255,0.2)"/>
            <text x="56" y="48" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="22">1</text>
          </g>
        `;
      }
      // All Mix: Neural Synaptic Web + Golden Laurel Question Badge
      return `
        <g opacity="0.45">
          <line x1="40" y1="40" x2="105" y2="25" stroke="var(--accent)" stroke-width="1.6"/>
          <line x1="105" y1="25" x2="160" y2="60" stroke="var(--accent)" stroke-width="1.6"/>
          <line x1="215" y1="25" x2="280" y2="40" stroke="#38BDF8" stroke-width="1.6"/>
          <circle cx="40" cy="40" r="4.5" fill="var(--accent)"/><circle cx="280" cy="40" r="4.5" fill="#38BDF8"/>
        </g>
        <g transform="translate(160, 60)">
          <circle cx="0" cy="0" r="46" fill="rgba(var(--accent-rgb),0.14)"/>
          <circle cx="0" cy="0" r="40" fill="#18181B" stroke="var(--accent)" stroke-width="2.5"/>
          <path d="M -30 12 C -35 -10 -24 -28 -10 -34" fill="none" stroke="#F59E0B" stroke-width="2.2" stroke-linecap="round"/>
          <path d="M 30 12 C 35 -10 24 -28 10 -34" fill="none" stroke="#F59E0B" stroke-width="2.2" stroke-linecap="round"/>
          <text x="0" y="16" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="800" font-size="48">?</text>
        </g>
      `;
    },

    // ------------------------------------------------------------------------
    // LUDO PROTOCOL (3 Unique Detailed Mode Icons)
    // ------------------------------------------------------------------------
    ludo: (i) => {
      if (i === 0) {
        // 1v1 Sprint: Opposite Crimson Red & Cobalt Blue Yards + Sculpted 3D Pawns Racing
        return `
          <g transform="translate(36, 16)">
            <rect x="0" y="0" width="76" height="76" rx="12" fill="rgba(239,68,68,0.18)" stroke="#EF4444" stroke-width="2"/>
            <ellipse cx="38" cy="56" rx="18" ry="6" fill="#991B1B"/>
            <path d="M 24 54 L 33 24 L 43 24 L 52 54 Z" fill="#EF4444" stroke="#FFF" stroke-width="1.2"/>
            <circle cx="38" cy="18" r="9.5" fill="#EF4444" stroke="#FFF" stroke-width="1.2"/>
          </g>
          <path d="M 118 54 L 202 54" stroke="#F59E0B" stroke-width="2.5" stroke-dasharray="6 4"/>
          <g transform="translate(208, 20)">
            <rect x="0" y="0" width="76" height="76" rx="12" fill="rgba(59,130,246,0.18)" stroke="#3B82F6" stroke-width="2"/>
            <ellipse cx="38" cy="56" rx="18" ry="6" fill="#1E40AF"/>
            <path d="M 24 54 L 33 24 L 43 24 L 52 54 Z" fill="#3B82F6" stroke="#FFF" stroke-width="1.2"/>
            <circle cx="38" cy="18" r="9.5" fill="#3B82F6" stroke="#FFF" stroke-width="1.2"/>
          </g>
        `;
      }
      if (i === 1) {
        // 4-Corner Chaos: Full 4-Quadrant Board Grid + Flared Crimson Pawn + Rolling Six Die
        return `
          <g transform="translate(34, 16)">
            <rect x="0" y="0" width="38" height="38" rx="6" fill="#EF4444" stroke="#FFF" stroke-width="1.4"/>
            <rect x="42" y="0" width="38" height="38" rx="6" fill="#10B981" stroke="#FFF" stroke-width="1.4"/>
            <rect x="0" y="42" width="38" height="38" rx="6" fill="#3B82F6" stroke="#FFF" stroke-width="1.4"/>
            <rect x="42" y="42" width="38" height="38" rx="6" fill="#EAB308" stroke="#FFF" stroke-width="1.4"/>
            <circle cx="19" cy="19" r="7" fill="#FFF"/><circle cx="61" cy="19" r="7" fill="#FFF"/>
            <circle cx="19" cy="61" r="7" fill="#FFF"/><circle cx="61" cy="61" r="7" fill="#FFF"/>
          </g>
          <g transform="translate(158, 24)">
            <ellipse cx="26" cy="70" rx="22" ry="7" fill="rgba(0,0,0,0.45)"/>
            <ellipse cx="26" cy="66" rx="20" ry="6" fill="#B91C1C"/>
            <path d="M 8 64 C 10 52 19 42 22 28 L 30 28 C 33 42 42 52 44 64 Z" fill="#EF4444" stroke="#991B1B" stroke-width="1.5"/>
            <circle cx="26" cy="18" r="11" fill="#EF4444" stroke="#991B1B" stroke-width="1.5"/>
          </g>
          <g transform="translate(226, 36) rotate(15)">
            <rect x="0" y="0" width="40" height="40" rx="8" fill="#FFF" stroke="#E4E4E7" stroke-width="2"/>
            <circle cx="11" cy="10" r="3" fill="#18181B"/><circle cx="11" cy="20" r="3" fill="#18181B"/><circle cx="11" cy="30" r="3" fill="#18181B"/>
            <circle cx="29" cy="10" r="3" fill="#18181B"/><circle cx="29" cy="20" r="3" fill="#18181B"/><circle cx="29" cy="30" r="3" fill="#18181B"/>
          </g>
        `;
      }
      // Host Multiplayer Race: Giant Central Finish Home Crown Pyramid + Orbiting Star Safe Zones
      return `
        <g transform="translate(160, 58)">
          <rect x="-44" y="-44" width="88" height="88" rx="12" fill="#18181B" stroke="#FFF" stroke-width="2.2"/>
          <polygon points="-44,-44 0,0 -44,44" fill="#EF4444"/>
          <polygon points="-44,-44 44,-44 0,0" fill="#10B981"/>
          <polygon points="44,-44 44,44 0,0" fill="#EAB308"/>
          <polygon points="-44,44 44,44 0,0" fill="#3B82F6"/>
          <circle cx="0" cy="0" r="14" fill="#FFF" stroke="#18181B" stroke-width="2"/>
          <polygon points="0,-9 3,-3 9,-3 4,1 6,8 0,4 -6,8 -4,1 -9,-3 -3,-3" fill="#EAB308"/>
        </g>
      `;
    },

    // ------------------------------------------------------------------------
    // DOMINOES (3 Unique Detailed Mode Icons)
    // ------------------------------------------------------------------------
    dominoes: (i) => {
      if (i === 0) {
        // Quick 50-Pt Sprint: Green Gaming Felt + L-Shaped [6|6] & [5|4] Ivory/Obsidian Tiles
        return `
          <circle cx="160" cy="60" r="64" fill="rgba(16,185,129,0.1)"/>
          <g transform="translate(106, 14) rotate(-10)">
            <rect x="4" y="4" width="48" height="94" rx="8" fill="rgba(0,0,0,0.5)"/>
            <rect x="0" y="0" width="48" height="94" rx="8" fill="#FAFAFA" stroke="#D4D4D8" stroke-width="2"/>
            <line x1="6" y1="47" x2="42" y2="47" stroke="#71717A" stroke-width="2"/>
            <circle cx="24" cy="47" r="2.6" fill="#EAB308"/>
            <circle cx="14" cy="14" r="3" fill="#18181B"/><circle cx="34" cy="14" r="3" fill="#18181B"/>
            <circle cx="14" cy="23.5" r="3" fill="#18181B"/><circle cx="34" cy="23.5" r="3" fill="#18181B"/>
            <circle cx="14" cy="33" r="3" fill="#18181B"/><circle cx="34" cy="33" r="3" fill="#18181B"/>
            <circle cx="14" cy="61" r="3" fill="#18181B"/><circle cx="34" cy="61" r="3" fill="#18181B"/>
            <circle cx="14" cy="70.5" r="3" fill="#18181B"/><circle cx="34" cy="70.5" r="3" fill="#18181B"/>
            <circle cx="14" cy="80" r="3" fill="#18181B"/><circle cx="34" cy="80" r="3" fill="#18181B"/>
          </g>
          <g transform="translate(174, 20) rotate(12)">
            <rect x="4" y="4" width="48" height="94" rx="8" fill="rgba(0,0,0,0.5)"/>
            <rect x="0" y="0" width="48" height="94" rx="8" fill="#18181B" stroke="#3F3F46" stroke-width="2"/>
            <line x1="6" y1="47" x2="42" y2="47" stroke="#52525B" stroke-width="2"/>
            <circle cx="24" cy="47" r="2.6" fill="#EAB308"/>
            <circle cx="14" cy="14" r="2.8" fill="#FFF"/><circle cx="34" cy="14" r="2.8" fill="#FFF"/><circle cx="24" cy="23.5" r="2.8" fill="#FFF"/><circle cx="14" cy="33" r="2.8" fill="#FFF"/><circle cx="34" cy="33" r="2.8" fill="#FFF"/>
            <circle cx="14" cy="61" r="2.8" fill="#FFF"/><circle cx="34" cy="61" r="2.8" fill="#FFF"/><circle cx="14" cy="80" r="2.8" fill="#FFF"/><circle cx="34" cy="80" r="2.8" fill="#FFF"/>
          </g>
        `;
      }
      if (i === 1) {
        // 4-Way Table: Center Spinner [6|6] Branched in All 4 Directions on Felt
        return `
          <rect x="40" y="14" width="240" height="94" rx="14" fill="rgba(16,185,129,0.08)" stroke="rgba(16,185,129,0.28)" stroke-dasharray="4 3"/>
          <g transform="translate(160, 61)">
            <!-- Left & Right Horizontal Tiles -->
            <rect x="-82" y="-14" width="54" height="28" rx="5" fill="#FAFAFA" stroke="#D4D4D8" stroke-width="1.5"/>
            <rect x="28" y="-14" width="54" height="28" rx="5" fill="#FAFAFA" stroke="#D4D4D8" stroke-width="1.5"/>
            <!-- Center Double Spinner -->
            <rect x="-24" y="-36" width="48" height="72" rx="7" fill="#18181B" stroke="#F59E0B" stroke-width="2"/>
            <line x1="-20" y1="0" x2="20" y2="0" stroke="#52525B" stroke-width="1.8"/>
            <circle cx="0" cy="0" r="3.5" fill="#F59E0B"/>
            <circle cx="-10" cy="-24" r="2.6" fill="#FFF"/><circle cx="10" cy="-24" r="2.6" fill="#FFF"/>
            <circle cx="-10" cy="-12" r="2.6" fill="#FFF"/><circle cx="10" cy="-12" r="2.6" fill="#FFF"/>
            <circle cx="-10" cy="12" r="2.6" fill="#FFF"/><circle cx="10" cy="12" r="2.6" fill="#FFF"/>
            <circle cx="-10" cy="24" r="2.6" fill="#FFF"/><circle cx="10" cy="24" r="2.6" fill="#FFF"/>
          </g>
        `;
      }
      // Host 2-4P Table: Carved Wooden Rack + Fanned Domino Hand + Boneyard Stack
      return `
        <g transform="translate(76, 16)">
          <rect x="0" y="14" width="40" height="76" rx="7" fill="#FAFAFA" stroke="#D4D4D8" stroke-width="1.8" transform="rotate(-14 20 52)"/>
          <rect x="44" y="4" width="40" height="76" rx="7" fill="#FAFAFA" stroke="#D4D4D8" stroke-width="1.8"/>
          <rect x="88" y="4" width="40" height="76" rx="7" fill="#FAFAFA" stroke="#D4D4D8" stroke-width="1.8"/>
          <rect x="132" y="14" width="40" height="76" rx="7" fill="#18181B" stroke="var(--accent)" stroke-width="2" transform="rotate(14 152 52)"/>
          <line x1="48" y1="42" x2="80" y2="42" stroke="#71717A" stroke-width="1.8"/>
          <circle cx="64" cy="42" r="2.6" fill="#EAB308"/>
          <line x1="92" y1="42" x2="124" y2="42" stroke="#71717A" stroke-width="1.8"/>
          <circle cx="108" cy="42" r="2.6" fill="#EAB308"/>
        </g>
        <rect x="46" y="90" width="228" height="10" rx="5" fill="#78350F" stroke="#F59E0B" stroke-width="1"/>
      `;
    },

    // ------------------------------------------------------------------------
    // SKRU (3 Unique Detailed Mode Icons)
    // ------------------------------------------------------------------------
    skru: (i) => {
      if (i === 0) {
        // 1v1 Memory Duel: Glowing Peek Eye + 2x2 Memory Grid with Revealed '0' Card
        return `
          <g transform="translate(56, 56)">
            <path d="M -30 0 Q 0 -18 30 0 Q 0 18 -30 0 Z" fill="rgba(var(--accent-rgb),0.18)" stroke="var(--accent)" stroke-width="2.2"/>
            <circle cx="0" cy="0" r="9" fill="#18181B" stroke="#FFF" stroke-width="1.5"/>
            <circle cx="0" cy="0" r="4.5" fill="var(--accent)"/>
          </g>
          <g transform="translate(132, 14)">
            <rect x="0" y="0" width="48" height="64" rx="7" fill="#18181B" stroke="rgba(255,255,255,0.22)"/>
            <rect x="58" y="0" width="48" height="64" rx="7" fill="#18181B" stroke="rgba(255,255,255,0.22)"/>
            <g transform="translate(0, 34)">
              <rect x="0" y="0" width="48" height="64" rx="7" fill="rgba(16,185,129,0.22)" stroke="#10B981" stroke-width="2"/>
              <text x="24" y="42" text-anchor="middle" fill="#10B981" font-family="'DM Sans',sans-serif" font-weight="900" font-size="28">0</text>
            </g>
            <g transform="translate(58, 34)">
              <rect x="0" y="0" width="48" height="64" rx="7" fill="rgba(var(--accent-rgb),0.26)" stroke="var(--accent)" stroke-width="2"/>
              <text x="24" y="42" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="28">1</text>
            </g>
          </g>
        `;
      }
      if (i === 1) {
        // 4P Party: Basra Card Exchange Curves Between +20 Crimson Card & Kaab Dayer King Card
        return `
          <g transform="translate(74, 18)">
            <rect x="0" y="14" width="58" height="80" rx="8" fill="rgba(239,68,68,0.24)" stroke="#EF4444" stroke-width="2.2" transform="rotate(-10 29 54)"/>
            <text x="29" y="60" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="20">+20</text>
            <path d="M 52 24 Q 86 0 118 24" fill="none" stroke="#F59E0B" stroke-width="2.8" stroke-linecap="round"/>
            <path d="M 118 82 Q 86 104 52 82" fill="none" stroke="#10B981" stroke-width="2.8" stroke-linecap="round"/>
            <rect x="114" y="14" width="58" height="80" rx="8" fill="#18181B" stroke="#38BDF8" stroke-width="2.2" transform="rotate(10 143 54)"/>
            <text x="143" y="60" text-anchor="middle" fill="#38BDF8" font-family="'DM Sans',sans-serif" font-weight="900" font-size="24">K</text>
          </g>
        `;
      }
      // Host 2-6P Skru Table: Fanned Deck Bursting with Crowned Red SKRU '0' Hero Card
      return `
        <g transform="translate(88, 16)">
          <rect x="0" y="10" width="54" height="78" rx="8" fill="#18181B" stroke="#D4D4D8" transform="rotate(-16 27 49)"/>
          <rect x="44" y="4" width="54" height="78" rx="8" fill="#27272A" stroke="#F59E0B" transform="rotate(-4 71 43)"/>
          <rect x="88" y="4" width="58" height="84" rx="9" fill="var(--accent)" stroke="#FFF" stroke-width="2.2" transform="rotate(10 117 46)"/>
          <text x="117" y="46" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="14">SKRU!</text>
          <text x="117" y="64" text-anchor="middle" fill="#FFF" font-family="'DM Sans',sans-serif" font-weight="900" font-size="16">0</text>
        </g>
      `;
    },

    // ------------------------------------------------------------------------
    // BACKGAMMON / TAWLA (4 Unique Detailed Mode Icons)
    // ------------------------------------------------------------------------
    backgammon: (i) => {
      if (i === 0) {
        // Mode 0: Classic Franjieh - Inlaid Walnut/Ivory Points + Grooved Stacked Checkers + Flying Blot onto Central Bar + Twin Dice
        return `
          <!-- Full Wooden Case Background Points (Top & Bottom) -->
          <g transform="translate(24, 6)">
            <polygon points="0,0 18,76 36,0" fill="rgba(var(--accent-rgb),0.58)" stroke="rgba(255,255,255,0.16)"/>
            <polygon points="36,0 54,76 72,0" fill="rgba(255,255,255,0.12)" stroke="rgba(255,255,255,0.16)"/>
            <polygon points="72,0 90,76 108,0" fill="rgba(var(--accent-rgb),0.58)" stroke="rgba(255,255,255,0.16)"/>
            <polygon points="108,0 126,76 144,0" fill="rgba(255,255,255,0.12)" stroke="rgba(255,255,255,0.16)"/>
          </g>
          <!-- Center Mahogany Bar with Brass Hinges & Stranded Checker -->
          <rect x="174" y="4" width="16" height="114" rx="3" fill="#27272A" stroke="#F59E0B" stroke-width="1"/>
          <ellipse cx="182" cy="54" rx="12" ry="12" fill="var(--accent)" stroke="#FFF" stroke-width="1.8"/>
          <!-- Stacked Grooved Bone & Ebony Checkers on Points -->
          <g transform="translate(42, 64)">
            <ellipse cx="0" cy="24" rx="18" ry="6" fill="#18181B" stroke="#52525B" stroke-width="1.4"/>
            <ellipse cx="0" cy="16" rx="18" ry="6" fill="#27272A" stroke="#52525B" stroke-width="1.4"/>
            <ellipse cx="0" cy="8" rx="18" ry="6" fill="#3F3F46" stroke="var(--color-bone)" stroke-width="1.5"/>
            <ellipse cx="0" cy="8" rx="10" ry="3" fill="none" stroke="rgba(255,255,255,0.35)"/>
          </g>
          <!-- Rolling Pair of Precision Dice -->
          <g transform="translate(214, 34) rotate(12)">
            <rect x="3" y="4" width="34" height="34" rx="7" fill="rgba(0,0,0,0.45)"/>
            <rect x="0" y="0" width="34" height="34" rx="7" fill="#FFF" stroke="#D4D4D8" stroke-width="1.8"/>
            <circle cx="9" cy="9" r="2.6" fill="#B91C1C"/><circle cx="25" cy="9" r="2.6" fill="#B91C1C"/>
            <circle cx="17" cy="17" r="2.6" fill="#B91C1C"/>
            <circle cx="9" cy="25" r="2.6" fill="#B91C1C"/><circle cx="25" cy="25" r="2.6" fill="#B91C1C"/>
            <g transform="translate(38, 8) rotate(-24)">
              <rect x="3" y="4" width="32" height="32" rx="7" fill="rgba(0,0,0,0.45)"/>
              <rect x="0" y="0" width="32" height="32" rx="7" fill="#FFF" stroke="#D4D4D8" stroke-width="1.8"/>
              <circle cx="9" cy="9" r="2.4" fill="#18181B"/><circle cx="16" cy="16" r="2.4" fill="#18181B"/><circle cx="23" cy="23" r="2.4" fill="#18181B"/>
            </g>
          </g>
        `;
      }
      if (i === 1) {
        // Mode 1: Tawla 31 - Towering 15-Checker Starting Gate + Golden Medallion '31' + Racing Trajectory
        return `
          <defs>
            <radialGradient id="g_bg_1" cx="72%" cy="50%" r="55%">
              <stop offset="0%" stop-color="#F59E0B" stop-opacity="0.28"/>
              <stop offset="100%" stop-color="#09090B" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <rect width="320" height="180" fill="url(#g_bg_1)"/>
          <!-- Starting Point Triangle Backdrop -->
          <polygon points="48,12 72,96 96,12" fill="rgba(245,158,11,0.3)" stroke="rgba(245,158,11,0.5)"/>
          <!-- Towering 15-Checker Column on Gate Point 24 -->
          <g transform="translate(72, 18)">
            <rect x="-20" y="74" width="40" height="10" rx="3" fill="#27272A" stroke="#F59E0B" stroke-width="1.2"/>
            <ellipse cx="0" cy="70" rx="18" ry="5.5" fill="#FAFAFA" stroke="#18181B" stroke-width="1.3"/>
            <ellipse cx="0" cy="61" rx="18" ry="5.5" fill="#E4E4E7" stroke="#18181B" stroke-width="1.3"/>
            <ellipse cx="0" cy="52" rx="18" ry="5.5" fill="#FAFAFA" stroke="#18181B" stroke-width="1.3"/>
            <ellipse cx="0" cy="43" rx="18" ry="5.5" fill="#E4E4E7" stroke="#18181B" stroke-width="1.3"/>
            <ellipse cx="0" cy="34" rx="18" ry="5.5" fill="#F59E0B" stroke="#FFF" stroke-width="1.4"/>
            <text x="0" y="21" text-anchor="middle" fill="#FDE047" font-family="'DM Sans',sans-serif" font-weight="900" font-size="12">×15</text>
          </g>
          <!-- Sweeping Golden Race Trajectory -->
          <path d="M 96 42 Q 145 8 190 36" fill="none" stroke="#F59E0B" stroke-width="3" stroke-dasharray="6 4"/>
          <!-- Embossed Championship Golden '31' Medallion -->
          <g transform="translate(226, 56)">
            <circle cx="0" cy="0" r="40" fill="#18181B" stroke="#F59E0B" stroke-width="3.5"/>
            <circle cx="0" cy="0" r="33" fill="rgba(245,158,11,0.16)" stroke="rgba(245,158,11,0.5)" stroke-dasharray="4 3"/>
            <text x="0" y="12" text-anchor="middle" fill="#FDE047" font-family="'DM Sans',sans-serif" font-weight="900" font-size="34">31</text>
          </g>
        `;
      }
      if (i === 2) {
        // Mode 2: Mahbosa (المحبوسة) - Pinned Ivory Checker Trapped Beneath Crimson Guard Checkers + Chains & Padlock
        return `
          <defs>
            <radialGradient id="g_bg_2" cx="55%" cy="50%" r="55%">
              <stop offset="0%" stop-color="#EF4444" stop-opacity="0.32"/>
              <stop offset="100%" stop-color="#09090B" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <rect width="320" height="180" fill="url(#g_bg_2)"/>
          <!-- Jail Point Triangle Backdrop -->
          <polygon points="96,10 154,112 212,10" fill="rgba(255,255,255,0.08)" stroke="rgba(239,68,68,0.4)" stroke-width="1.5"/>
          <!-- Pinned Ivory Checker Locked Beneath Heavy Crimson Checker -->
          <g transform="translate(154, 66)">
            <ellipse cx="0" cy="22" rx="34" ry="12" fill="rgba(0,0,0,0.6)"/>
            <!-- Imprisoned Cream Checker Bottom -->
            <ellipse cx="0" cy="14" rx="32" ry="11" fill="#FAFAFA" stroke="#EF4444" stroke-width="2.5"/>
            <!-- Heavy Crimson Pinning Checker On Top -->
            <ellipse cx="0" cy="-2" rx="32" ry="11" fill="#B91C1C" stroke="#FFF" stroke-width="2"/>
            <ellipse cx="0" cy="-6" rx="20" ry="6" fill="none" stroke="rgba(255,255,255,0.45)" stroke-width="1.2"/>
            <!-- Interlocking Iron Chains Over Stack -->
            <line x1="-28" y1="14" x2="28" y2="-10" stroke="#F59E0B" stroke-width="3.6" stroke-dasharray="5 3"/>
            <line x1="-28" y1="-10" x2="28" y2="14" stroke="#F59E0B" stroke-width="3.6" stroke-dasharray="5 3"/>
          </g>
          <!-- Brass Padlock Seal -->
          <g transform="translate(216, 28)">
            <path d="M 8 16 L 8 8 C 8 1 24 1 24 8 L 24 16" fill="none" stroke="#FDE047" stroke-width="3.2"/>
            <rect x="2" y="16" width="28" height="22" rx="5" fill="#F59E0B" stroke="#FFF" stroke-width="1.5"/>
            <circle cx="16" cy="25" r="3" fill="#18181B"/>
            <line x1="16" y1="27" x2="16" y2="33" stroke="#18181B" stroke-width="2.4" stroke-linecap="round"/>
          </g>
        `;
      }
      // Mode 3: Host 2P Tawla Room - Facing Leather Dice Cups + Twin Tournament Dice [6][6] + Checker Formations
      return `
        <!-- Open Board Divider Line -->
        <line x1="160" y1="8" x2="160" y2="120" stroke="rgba(255,255,255,0.18)" stroke-width="2" stroke-dasharray="5 3"/>
        <!-- Left & Right Hand-Stitched Leather Cups -->
        <g transform="translate(54, 24) rotate(-8)">
          <path d="M 4 12 L 42 12 L 36 66 L 10 66 Z" fill="#27272A" stroke="#F59E0B" stroke-width="2.2"/>
          <ellipse cx="23" cy="12" rx="19" ry="5" fill="#18181B" stroke="#F59E0B" stroke-width="1.6"/>
        </g>
        <g transform="translate(220, 24) rotate(8)">
          <path d="M 4 12 L 42 12 L 36 66 L 10 66 Z" fill="#27272A" stroke="var(--accent)" stroke-width="2.2"/>
          <ellipse cx="23" cy="12" rx="19" ry="5" fill="#18181B" stroke="var(--accent)" stroke-width="1.6"/>
        </g>
        <!-- Championship Double-Six Dice -->
        <g transform="translate(120, 38) rotate(-10)">
          <rect x="2" y="4" width="34" height="34" rx="7" fill="rgba(0,0,0,0.45)"/>
          <rect x="0" y="0" width="34" height="34" rx="7" fill="#FFF" stroke="#D4D4D8" stroke-width="1.8"/>
          <circle cx="9" cy="8" r="2.5" fill="#B91C1C"/><circle cx="9" cy="17" r="2.5" fill="#B91C1C"/><circle cx="9" cy="26" r="2.5" fill="#B91C1C"/>
          <circle cx="25" cy="8" r="2.5" fill="#B91C1C"/><circle cx="25" cy="17" r="2.5" fill="#B91C1C"/><circle cx="25" cy="26" r="2.5" fill="#B91C1C"/>
        </g>
        <g transform="translate(168, 44) rotate(14)">
          <rect x="2" y="4" width="34" height="34" rx="7" fill="rgba(0,0,0,0.45)"/>
          <rect x="0" y="0" width="34" height="34" rx="7" fill="#FFF" stroke="#D4D4D8" stroke-width="1.8"/>
          <circle cx="9" cy="8" r="2.5" fill="#18181B"/><circle cx="9" cy="17" r="2.5" fill="#18181B"/><circle cx="9" cy="26" r="2.5" fill="#18181B"/>
          <circle cx="25" cy="8" r="2.5" fill="#18181B"/><circle cx="25" cy="17" r="2.5" fill="#18181B"/><circle cx="25" cy="26" r="2.5" fill="#18181B"/>
        </g>
      `;
    },

    // ------------------------------------------------------------------------
    // TIC-TAC-TOE
    // ------------------------------------------------------------------------
    tic_tac_toe: (i) => {
      if (i === 1) {
        // Misère Mode: 3-in-a-row loses
        return `
          <path d="M 106 30 L 106 150 M 213 30 L 213 150 M 50 70 L 270 70 M 50 110 L 270 110" stroke="rgba(255,255,255,0.1)" stroke-width="2" stroke-linecap="round"/>
          <g stroke="#EF4444" stroke-width="4" stroke-linecap="round">
            <line x1="70" y1="42" x2="88" y2="58"/><line x1="88" y1="42" x2="70" y2="58"/>
            <line x1="151" y1="42" x2="169" y2="58"/><line x1="169" y1="42" x2="151" y2="58"/>
            <line x1="232" y1="42" x2="250" y2="58"/><line x1="250" y1="42" x2="232" y2="58"/>
          </g>
          <line x1="55" y1="50" x2="265" y2="50" stroke="#EF4444" stroke-width="3" stroke-dasharray="6 4"/>
          <g transform="translate(160, 130)">
            <rect x="-65" y="-14" width="130" height="28" rx="14" fill="#18181B" stroke="#EF4444" stroke-width="1.5"/>
            <text x="0" y="4" text-anchor="middle" fill="#EF4444" font-family="'DM Sans', sans-serif" font-weight="800" font-size="11" letter-spacing="0.5">3-IN-A-ROW LOSES</text>
          </g>
        `;
      }
      if (i === 2) {
        // Extended 4x4 Grid
        return `
          <g stroke="rgba(255,255,255,0.12)" stroke-width="1.5">
            <line x1="110" y1="20" x2="110" y2="160"/><line x1="160" y1="20" x2="160" y2="160"/><line x1="210" y1="20" x2="210" y2="160"/>
            <line x1="60" y1="55" x2="260" y2="55"/><line x1="60" y1="90" x2="260" y2="90"/><line x1="60" y1="125" x2="260" y2="125"/>
          </g>
          ${[0, 1, 2, 3].map(step => `
            <circle cx="${85 + step * 50}" cy="${37.5 + step * 35}" r="11" fill="var(--accent)" stroke="#fff" stroke-width="1.5"/>
          `).join('')}
          <line x1="75" y1="30" x2="245" y2="150" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>
          <g transform="translate(160, 165)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">4×4 GRID · 4-IN-A-ROW</text>
          </g>
        `;
      }
      if (i === 3) {
        // Extended 5x5 Grid
        return `
          <g stroke="rgba(255,255,255,0.08)" stroke-width="1.2">
            ${[100, 130, 160, 190].map(x => `<line x1="${x}" y1="20" x2="${x}" y2="150"/>`).join('')}
            ${[46, 72, 98, 124].map(y => `<line x1="70" y1="${y}" x2="220" y2="${y}"/>`).join('')}
          </g>
          ${[0, 1, 2, 3].map(step => `
            <rect x="${105 + step * 30}" y="77" width="20" height="16" rx="4" fill="var(--accent)"/>
          `).join('')}
          <line x1="100" y1="85" x2="225" y2="85" stroke="#fff" stroke-width="2"/>
          <g transform="translate(160, 165)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">5×5 MATRIX · SLIDING 4</text>
          </g>
        `;
      }
      if (i === 4) {
        // Ultimate Tic-Tac-Toe
        return `
          <g stroke="var(--accent)" stroke-width="3" stroke-linecap="round">
            <line x1="120" y1="20" x2="120" y2="160"/><line x1="200" y1="20" x2="200" y2="160"/>
            <line x1="40" y1="66" x2="280" y2="66"/><line x1="40" y1="114" x2="280" y2="114"/>
          </g>
          <rect x="125" y="71" width="70" height="38" rx="6" fill="rgba(56,189,248,0.22)" stroke="var(--accent)" stroke-width="2" stroke-dasharray="4 2"/>
          <path d="M 80 43 Q 120 40 160 85" fill="none" stroke="#F59E0B" stroke-width="2" stroke-dasharray="4 3"/>
          <circle cx="80" cy="43" r="3" fill="#F59E0B"/>
          <polygon points="160,85 152,78 156,88" fill="#F59E0B"/>
          <text x="80" y="100" text-anchor="middle" fill="var(--accent)" font-family="'DM Sans', sans-serif" font-weight="900" font-size="28" opacity="0.8">X</text>
          <text x="240" y="55" text-anchor="middle" fill="#EF4444" font-family="'DM Sans', sans-serif" font-weight="900" font-size="28" opacity="0.8">O</text>
          <g transform="translate(160, 168)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">ULTIMATE · TARGET ROUTING</text>
          </g>
        `;
      }
      // Default / idx === 0: Classic 3x3 Minimax
      return `
        <g stroke="rgba(255,255,255,0.15)" stroke-width="2" stroke-linecap="round">
          <line x1="120" y1="25" x2="120" y2="155"/><line x1="200" y1="25" x2="200" y2="155"/>
          <line x1="45" y1="68" x2="275" y2="68"/><line x1="45" y1="112" x2="275" y2="112"/>
        </g>
        <g stroke="var(--accent)" stroke-width="4.5" stroke-linecap="round">
          <line x1="68" y1="36" x2="96" y2="58"/><line x1="96" y1="36" x2="68" y2="58"/>
          <line x1="148" y1="78" x2="172" y2="102"/><line x1="172" y1="78" x2="148" y2="102"/>
          <line x1="228" y1="122" x2="252" y2="146"/><line x1="252" y1="122" x2="228" y2="146"/>
        </g>
        <circle cx="160" cy="47" r="14" fill="none" stroke="#F59E0B" stroke-width="4"/>
        <circle cx="82" cy="90" r="14" fill="none" stroke="#F59E0B" stroke-width="4"/>
        <line x1="55" y1="25" x2="265" y2="155" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
        <g transform="translate(250, 40)">
          <rect x="-35" y="-12" width="70" height="24" rx="6" fill="#18181B" stroke="var(--accent)" stroke-width="1.2"/>
          <text x="0" y="4" text-anchor="middle" fill="var(--accent)" font-family="'DM Sans', sans-serif" font-weight="800" font-size="9">MINIMAX</text>
        </g>
      `;
    },
    rock_paper_scissors: (i) => {
      if (i === 1) {
        // RPSLS 5-Choice Pentagram
        return `
          <g transform="translate(160, 85)">
            <polygon points="0,-55 52,-17 32,45 -32,45 -52,-17" fill="rgba(16,185,129,0.12)" stroke="var(--accent)" stroke-width="2"/>
            <polygon points="0,-55 32,45 -52,-17 52,-17 -32,45" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-dasharray="3 2" opacity="0.6"/>
            <circle cx="0" cy="-55" r="7" fill="#18181B" stroke="var(--accent)" stroke-width="2"/>
            <circle cx="52" cy="-17" r="7" fill="#18181B" stroke="#fff" stroke-width="1.5"/>
            <circle cx="32" cy="45" r="7" fill="#18181B" stroke="var(--accent)" stroke-width="2"/>
            <circle cx="-32" cy="45" r="7" fill="#18181B" stroke="#fff" stroke-width="1.5"/>
            <circle cx="-52" cy="-17" r="7" fill="#18181B" stroke="var(--accent)" stroke-width="2"/>
          </g>
          <g transform="translate(160, 168)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">RPSLS · 5-WEAPON GRAPH</text>
          </g>
        `;
      }
      if (i === 2) {
        // Endless Streak Flame
        return `
          <g transform="translate(160, 78)">
            <circle cx="0" cy="0" r="38" fill="rgba(245,158,11,0.12)" stroke="#F59E0B" stroke-width="2"/>
            <path d="M0 -24 C10 -10 18 -4 14 12 C10 24 -10 24 -14 12 C-18 -4 -10 -10 0 -24 Z" fill="#F59E0B" opacity="0.85"/>
            <path d="M0 -12 C5 -4 9 0 7 8 C5 14 -5 14 -7 8 C-9 0 -5 -4 0 -12 Z" fill="#fff"/>
          </g>
          <g transform="translate(160, 168)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">ENDLESS STREAK · FLAME CHALLENGE</text>
          </g>
        `;
      }
      if (i === 3) {
        // 2P Host Duel
        return `
          <g transform="translate(160, 80)">
            <circle cx="-45" cy="0" r="28" fill="rgba(18,18,24,0.8)" stroke="var(--accent)" stroke-width="2"/>
            <circle cx="45" cy="0" r="28" fill="rgba(18,18,24,0.8)" stroke="#fff" stroke-width="2"/>
            <text x="-45" y="7" text-anchor="middle" fill="var(--accent)" font-family="'DM Sans', sans-serif" font-weight="900" font-size="16">P1</text>
            <text x="45" y="7" text-anchor="middle" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="900" font-size="16">P2</text>
            <circle cx="0" cy="0" r="10" fill="#18181B" stroke="var(--accent)" stroke-width="1.5"/>
            <text x="0" y="4" text-anchor="middle" fill="#F59E0B" font-family="'DM Sans', sans-serif" font-weight="800" font-size="10">VS</text>
          </g>
          <g transform="translate(160, 168)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">2-PLAYER · HEAD-TO-HEAD DUEL</text>
          </g>
        `;
      }
      // Default / i === 0: Classic Rock vs Scissors
      return `
        <g transform="translate(160, 78)">
          <circle cx="-42" cy="0" r="32" fill="rgba(18,18,24,0.85)" stroke="var(--accent)" stroke-width="2.2"/>
          <circle cx="42" cy="0" r="32" fill="rgba(18,18,24,0.85)" stroke="#fff" stroke-width="2.2"/>
          <text x="-42" y="8" text-anchor="middle" font-size="22">✊</text>
          <text x="42" y="8" text-anchor="middle" font-size="22">✌️</text>
          <line x1="-10" y1="0" x2="10" y2="0" stroke="var(--accent)" stroke-width="2.5" stroke-linecap="round"/>
        </g>
        <g transform="translate(160, 168)">
          <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">CLASSIC BEST-OF-3</text>
        </g>
      `;
    },
    connect4: (i) => {
      if (i === 1) {
        // Pop Out Mode: bottom disc ejection
        return `
          <g transform="translate(160, 75)">
            <rect x="-80" y="-55" width="160" height="110" rx="12" fill="rgba(20,24,36,0.85)" stroke="var(--color-hairline)"/>
            <!-- 3 Columns of Cutouts -->
            ${[-45, 0, 45].map(x => `
              <circle cx="${x}" cy="-25" r="14" fill="#08090e" stroke="rgba(255,255,255,0.1)"/>
              <circle cx="${x}" cy="10" r="14" fill="#08090e" stroke="rgba(255,255,255,0.1)"/>
            `).join('')}
            <circle cx="-45" cy="-25" r="12" fill="#ff4034"/>
            <circle cx="0" cy="-25" r="12" fill="#facc15"/>
            <circle cx="45" cy="-25" r="12" fill="#ff4034"/>
            <circle cx="-45" cy="10" r="12" fill="#facc15"/>
            <circle cx="45" cy="10" r="12" fill="#facc15"/>
            <!-- Popped Disc falling out bottom -->
            <g transform="translate(0, 38)">
              <circle cx="0" cy="0" r="12" fill="#ff4034" filter="drop-shadow(0 0 8px rgba(255,64,52,0.8))"/>
              <text x="0" y="4" text-anchor="middle" fill="#fff" font-size="10" font-weight="900">⏏</text>
            </g>
          </g>
          <g transform="translate(160, 168)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">POP OUT · GRAVITY SHIFT</text>
          </g>
        `;
      }
      if (i === 2) {
        // 5-in-a-Row 9x7 Matrix
        return `
          <g transform="translate(160, 75)">
            <rect x="-100" y="-55" width="200" height="110" rx="12" fill="rgba(20,24,36,0.85)" stroke="var(--color-hairline)"/>
            <!-- 5 connected discs -->
            ${[-60, -30, 0, 30, 60].map(x => `
              <circle cx="${x}" cy="10" r="11" fill="#ff4034" filter="drop-shadow(0 0 6px rgba(255,64,52,0.7))"/>
            `).join('')}
            <!-- Connecting laser -->
            <line x1="-60" y1="10" x2="60" y2="10" stroke="#ff4034" stroke-width="2.5" filter="drop-shadow(0 0 6px rgba(255,64,52,0.9))"/>
            <!-- Background slots -->
            ${[-60, -30, 0, 30, 60].map(x => `
              <circle cx="${x}" cy="-20" r="11" fill="#08090e" stroke="rgba(255,255,255,0.08)"/>
            `).join('')}
            <circle cx="0" cy="-20" r="9" fill="#facc15"/>
          </g>
          <g transform="translate(160, 168)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">5-IN-A-ROW · 9×7 EXPANDED</text>
          </g>
        `;
      }
      if (i === 3) {
        // Blitz Mode: Lightning countdown
        return `
          <g transform="translate(160, 75)">
            <circle cx="0" cy="0" r="42" fill="rgba(20,24,36,0.9)" stroke="var(--c4-yellow)" stroke-width="2.5" stroke-dasharray="8 4"/>
            <circle cx="0" cy="0" r="32" fill="#ff4034" filter="drop-shadow(0 0 12px rgba(255,64,52,0.8))"/>
            <text x="0" y="8" text-anchor="middle" font-size="24">⚡</text>
          </g>
          <g transform="translate(160, 168)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">BLITZ · 5S COUNTDOWN</text>
          </g>
        `;
      }
      if (i === 4) {
        // Host 2P Multiplayer Room
        return `
          <g transform="translate(160, 78)">
            <circle cx="-42" cy="0" r="28" fill="#ff4034" filter="drop-shadow(0 0 10px rgba(255,64,52,0.7))"/>
            <circle cx="42" cy="0" r="28" fill="#facc15" filter="drop-shadow(0 0 10px rgba(250,204,21,0.7))"/>
            <text x="-42" y="6" text-anchor="middle" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="900" font-size="15">RED</text>
            <text x="42" y="6" text-anchor="middle" fill="#000" font-family="'DM Sans', sans-serif" font-weight="900" font-size="14">YEL</text>
            <circle cx="0" cy="0" r="12" fill="#141722" stroke="var(--color-hairline)" stroke-width="1.5"/>
            <text x="0" y="4" text-anchor="middle" fill="#fff" font-family="'DM Sans', sans-serif" font-weight="800" font-size="9">VS</text>
          </g>
          <g transform="translate(160, 168)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">2-PLAYER · ONLINE / PASS & PLAY</text>
          </g>
        `;
      }
      // Default / i === 0: Classic 7x6 4-Streak
      return `
        <g transform="translate(160, 75)">
          <rect x="-80" y="-55" width="160" height="110" rx="12" fill="rgba(20,24,36,0.85)" stroke="var(--color-hairline)"/>
          <!-- Diagonal 4-Streak -->
          <circle cx="-45" cy="25" r="12" fill="#ff4034" filter="drop-shadow(0 0 8px rgba(255,64,52,0.8))"/>
          <circle cx="-15" cy="0" r="12" fill="#ff4034" filter="drop-shadow(0 0 8px rgba(255,64,52,0.8))"/>
          <circle cx="15" cy="-25" r="12" fill="#ff4034" filter="drop-shadow(0 0 8px rgba(255,64,52,0.8))"/>
          <circle cx="45" cy="-50" r="12" fill="#ff4034" filter="drop-shadow(0 0 10px rgba(255,64,52,0.9))"/>
          <line x1="-45" y1="25" x2="45" y2="-50" stroke="#ff4034" stroke-width="3" stroke-linecap="round" filter="drop-shadow(0 0 8px rgba(255,64,52,0.9))"/>
          <!-- Other slots -->
          <circle cx="-45" cy="0" r="12" fill="#facc15"/>
          <circle cx="-15" cy="25" r="12" fill="#facc15"/>
          <circle cx="15" cy="0" r="12" fill="#facc15"/>
        </g>
        <g transform="translate(160, 168)">
          <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">CLASSIC 7×6 · 4-IN-A-ROW</text>
        </g>
      `;
    },
    playing_cards: (i) => {
      if (i === 1) {
        // War: Swords clash & cards
        return `
          <g transform="translate(160, 75)">
            <rect x="-65" y="-45" width="55" height="85" rx="6" fill="#181824" stroke="rgba(255,255,255,0.2)"/>
            <text x="-48" y="-20" fill="#38bdf8" font-size="14" font-weight="900">A♠</text>
            <rect x="10" y="-45" width="55" height="85" rx="6" fill="#181824" stroke="rgba(255,255,255,0.2)"/>
            <text x="28" y="-20" fill="#e5484d" font-size="14" font-weight="900">K♥</text>
            <text x="0" y="5" text-anchor="middle" font-size="28">⚔️</text>
          </g>
          <g transform="translate(160, 168)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">WAR · HIGH CARD BATTLE</text>
          </g>
        `;
      }
      if (i === 2) {
        // Memory: 3D flipped grid
        return `
          <g transform="translate(160, 75)">
            <rect x="-60" y="-40" width="35" height="50" rx="4" fill="#181824" stroke="#10b981" stroke-width="1.5"/>
            <text x="-43" y="-10" text-anchor="middle" fill="#10b981" font-size="16" font-weight="900">Q♦</text>
            <rect x="-17" y="-40" width="35" height="50" rx="4" fill="#181824" stroke="#10b981" stroke-width="1.5"/>
            <text x="0" y="-10" text-anchor="middle" fill="#10b981" font-size="16" font-weight="900">Q♦</text>
            <rect x="25" y="-40" width="35" height="50" rx="4" fill="#0d0d14" stroke="rgba(255,255,255,0.15)"/>
            <text x="42" y="-10" text-anchor="middle" fill="var(--accent)" font-size="16">🂠</text>
          </g>
          <g transform="translate(160, 168)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">MEMORY · CONCENTRATION</text>
          </g>
        `;
      }
      if (i === 3) {
        // High-Low: Up/Down arrow multipliers
        return `
          <g transform="translate(160, 75)">
            <rect x="-35" y="-50" width="70" height="95" rx="8" fill="#181824" stroke="var(--cards-diamond, #f59e0b)" stroke-width="2"/>
            <text x="-20" y="-25" fill="#f59e0b" font-size="16" font-weight="900">8♦</text>
            <text x="0" y="10" text-anchor="middle" font-size="26">⬆️</text>
            <text x="0" y="32" text-anchor="middle" fill="#f59e0b" font-size="13" font-weight="900">12.0×</text>
          </g>
          <g transform="translate(160, 168)">
            <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">HIGH-LOW · STREAK MULTIPLIER</text>
          </g>
        `;
      }
      // Default / i === 0: Blackjack
      return `
        <g transform="translate(160, 75)">
          <rect x="-55" y="-45" width="55" height="85" rx="6" fill="#181824" stroke="rgba(255,255,255,0.2)"/>
          <text x="-38" y="-20" fill="#38bdf8" font-size="14" font-weight="900">A♠</text>
          <rect x="-10" y="-45" width="55" height="85" rx="6" fill="#181824" stroke="rgba(255,255,255,0.2)"/>
          <text x="8" y="-20" fill="#e5484d" font-size="14" font-weight="900">J♥</text>
          <g transform="translate(45, 15)">
            <circle cx="0" cy="0" r="16" fill="#f59e0b" stroke="#fff" stroke-width="1.2" stroke-dasharray="3 2"/>
            <text x="0" y="4" text-anchor="middle" fill="#000" font-size="9" font-weight="900">21</text>
          </g>
        </g>
        <g transform="translate(160, 168)">
          <text x="0" y="0" text-anchor="middle" fill="var(--color-bone)" font-family="'DM Sans', sans-serif" font-weight="700" font-size="11">BLACKJACK · 21 VS DEALER</text>
        </g>
      `;
    },
  };

  const fn = generators[gameType] || generators.chess;
  const content = fn(idx);
  return `<svg viewBox="0 0 320 180" preserveAspectRatio="xMidYMid slice"><rect width="320" height="180" fill="rgba(18,18,22,0.45)"/>${content}</svg>`;
}
