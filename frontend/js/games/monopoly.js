import { escapeHtml, getActivePlayers } from '/js/utils.js?v=20261112';

const VALID_GROUPS = new Set([
  'brown', 'light_blue', 'pink', 'orange', 'red', 'yellow', 'green', 'dark_blue',
]);

function tileGridPos(id) {
  if (id <= 10) return { row: 11, col: 11 - id };
  if (id <= 20) return { row: 11 - (id - 10), col: 1 };
  if (id <= 30) return { row: 1, col: 1 + (id - 20) };
  return { row: 1 + (id - 30), col: 11 };
}

function buildPropCheckbox(tile, isMortgaged) {
  const lbl = document.createElement('label');
  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.value = String(tile.id);
  lbl.appendChild(cb);
  lbl.appendChild(document.createTextNode(` ${tile.name}${isMortgaged ? ' [MORTGAGED]' : ''}`));
  return lbl;
}

export function mount(container, { sendAction, sound, getPlayerId, getPlayers }) {
  let selectedTileId = null;
  let latestState = {};
  let latestPlayers = getPlayers() || [];
  let boardBuilt = false;
  const tileNodes = new Map();
  let centerTitleEl = null;
  let centerNoteEl = null;
  let centerActionsEl = null;
  let lastCenterSig = '';
  let auctionTitleEl = null;
  let auctionBidEl = null;
  let auctionBtnsEl = null;
  let lastAuctionBtnsSig = '';

  container.innerHTML = `
    <div class="game-shell">
      <div class="monopoly-layout">
        <div id="mo-board" class="monopoly-board"></div>

        <aside class="mono-side-panel">
          <div class="bunker-sublabel">PLAYERS &amp; CASH</div>
          <div id="mo-players" class="mono-players-list"></div>

          <div id="mo-trade-offer" class="clue-item hidden"></div>

          <div class="mono-trade-trigger-row">
            <button type="button" id="mo-open-trade" class="pill-btn pill-btn-sm">PROPOSE TRADE</button>
          </div>

          <div class="bunker-sublabel">PROPERTY INSPECTOR</div>
          <div id="mo-prop-panel" class="clue-item mono-prop-panel">
            Click any tile on the board to inspect, build houses, or mortgage.
          </div>
        </aside>
      </div>

      <div id="mo-trade-modal" class="modal-overlay hidden">
        <div class="modal-box">
          <div class="modal-top-bar">
            <h3 class="heading">TRADE PROPOSAL</h3>
            <button type="button" id="mo-trade-close" class="pill-btn pill-btn-sm">CLOSE</button>
          </div>
          <div class="setting-field">
            <label for="mo-trade-partner">TRADE PARTNER</label>
            <select id="mo-trade-partner" name="trade_partner" class="setting-select"></select>
          </div>
          <div class="mono-trade-grid">
            <div>
              <label for="mo-offer-cash" class="bunker-sublabel mono-trade-col-label">YOU OFFER</label>
              <input id="mo-offer-cash" name="offer_cash" class="text-input mono-trade-cash-input" type="number" min="0" value="0" placeholder="Cash $" />
              <div id="mo-offer-props" class="mono-trade-props-list"></div>
            </div>
            <div>
              <label for="mo-req-cash" class="bunker-sublabel mono-trade-col-label">YOU REQUEST</label>
              <input id="mo-req-cash" name="request_cash" class="text-input mono-trade-cash-input" type="number" min="0" value="0" placeholder="Cash $" />
              <div id="mo-req-props" class="mono-trade-props-list"></div>
            </div>
          </div>
          <button type="button" id="mo-trade-send" class="pill-btn pill-btn-md">SEND TRADE OFFER</button>
        </div>
      </div>
    </div>
  `;

  const boardEl = container.querySelector('#mo-board');
  const playersEl = container.querySelector('#mo-players');
  const tradeOfferEl = container.querySelector('#mo-trade-offer');
  const propPanel = container.querySelector('#mo-prop-panel');
  const openTradeBtn = container.querySelector('#mo-open-trade');
  const tradeModal = container.querySelector('#mo-trade-modal');
  const tradeCloseBtn = container.querySelector('#mo-trade-close');
  const tradePartnerSel = container.querySelector('#mo-trade-partner');
  const offerCashInput = container.querySelector('#mo-offer-cash');
  const reqCashInput = container.querySelector('#mo-req-cash');
  const offerPropsEl = container.querySelector('#mo-offer-props');
  const reqPropsEl = container.querySelector('#mo-req-props');
  const tradeSendBtn = container.querySelector('#mo-trade-send');

  const onOpenTrade = () => {
    if (openTradeBtn.disabled) return;
    sound.click();
    populateTradeModal();
    tradeModal.classList.remove('hidden');
  };
  const onCloseTrade = () => {
    sound.click();
    tradeModal.classList.add('hidden');
  };
  const onPartnerChange = () => renderTradePartnerProps();
  const onSendTrade = () => {
    if (!tradePartnerSel.value) return;
    sound.click();
    const offerProps = [...offerPropsEl.querySelectorAll('input:checked')].map((i) => Number(i.value));
    const reqProps = [...reqPropsEl.querySelectorAll('input:checked')].map((i) => Number(i.value));
    sendAction('propose_trade', {
      to_id: tradePartnerSel.value,
      offer_cash: Math.max(0, Number(offerCashInput.value || 0)),
      request_cash: Math.max(0, Number(reqCashInput.value || 0)),
      offer_props: offerProps,
      request_props: reqProps,
    });
    tradeModal.classList.add('hidden');
  };

  openTradeBtn.addEventListener('click', onOpenTrade);
  tradeCloseBtn.addEventListener('click', onCloseTrade);
  tradePartnerSel.addEventListener('change', onPartnerChange);
  tradeSendBtn.addEventListener('click', onSendTrade);

  function populateTradeModal() {
    const meId = getPlayerId();
    const activePlayers = getActivePlayers(latestPlayers);
    const pState = latestState.players_state || {};

    offerCashInput.value = '0';
    reqCashInput.value = '0';

    tradePartnerSel.innerHTML = '';
    for (const p of activePlayers) {
      if (p.id === meId || pState[p.id]?.bankrupt) continue;
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = `${p.name} ($${Number(pState[p.id]?.cash ?? 0)})`;
      tradePartnerSel.appendChild(opt);
    }
    tradeSendBtn.disabled = !tradePartnerSel.value;

    const board = latestState.board || [];
    const ownership = latestState.ownership || {};
    const houses = latestState.houses || {};
    const mortgaged = new Set(latestState.mortgaged || []);
    offerPropsEl.innerHTML = '';
    board.forEach((t) => {
      if (ownership[String(t.id)] === meId && !(houses[String(t.id)] > 0)) {
        offerPropsEl.appendChild(buildPropCheckbox(t, mortgaged.has(t.id)));
      }
    });
    renderTradePartnerProps();
  }

  function renderTradePartnerProps() {
    const pid = tradePartnerSel.value;
    const board = latestState.board || [];
    const ownership = latestState.ownership || {};
    const houses = latestState.houses || {};
    const mortgaged = new Set(latestState.mortgaged || []);
    reqPropsEl.innerHTML = '';
    if (!pid) return;
    board.forEach((t) => {
      if (ownership[String(t.id)] === pid && !(houses[String(t.id)] > 0)) {
        reqPropsEl.appendChild(buildPropCheckbox(t, mortgaged.has(t.id)));
      }
    });
  }

  function makeSmallBtn(label, onClick, disabled = false) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'pill-btn pill-btn-sm';
    b.textContent = label;
    b.disabled = disabled;
    b.addEventListener('click', () => {
      sound.click();
      onClick();
    });
    return b;
  }

  function renderInspector(tile) {
    if (!tile) return;
    const meId = getPlayerId();
    const me = latestPlayers.find((p) => p.id === meId);
    const isSpectator = Boolean(!me || me.role === 'spectator');
    const activePlayers = getActivePlayers(latestPlayers);
    const board = latestState.board || [];
    const pState = latestState.players_state || {};
    const mySt = pState[meId] || {};
    const ownership = latestState.ownership || {};
    const houses = latestState.houses || {};
    const mortgaged = new Set(latestState.mortgaged || []);

    const ownerId = ownership[String(tile.id)];
    const ownerP = activePlayers.find((p) => p.id === ownerId);
    const hCount = houses[String(tile.id)] || 0;
    const isMort = mortgaged.has(tile.id);

    const groupDot = tile.group && VALID_GROUPS.has(tile.group)
      ? `<span class="mono-color-bar mono-group-${tile.group}"></span> `
      : '';
    let html = `${groupDot}<strong>${escapeHtml(tile.name)}</strong><br/>`;
    if (tile.price) html += `Price: $${Number(tile.price)} · `;
    html += ownerP ? `Owner: ${escapeHtml(ownerP.name)}` : 'Unowned';
    if (isMort) html += ' · <strong class="mono-mortgaged-tag">MORTGAGED</strong>';

    if (tile.kind === 'prop') {
      html += `<br/>Houses: ${hCount === 5 ? 'HOTEL' : hCount} · House Cost: $${Number(tile.house_cost)}`;
      if (Array.isArray(tile.rent) && tile.rent.length >= 6) {
        const r = tile.rent.map((n) => Number(n) || 0);
        html += `<br/>Rent: Base $${r[0]} (Set $${r[0] * 2}) · 1H $${r[1]} · 2H $${r[2]} · 3H $${r[3]} · 4H $${r[4]} · Hotel $${r[5]}`;
      }
    } else if (tile.kind === 'railroad') {
      html += '<br/>Rent: 1 RR $25 · 2 RR $50 · 3 RR $100 · 4 RR $200';
    } else if (tile.kind === 'utility') {
      html += '<br/>Rent: 1 Utility 4× Dice · Both 10× Dice';
    } else if (tile.kind === 'tax' && tile.amount) {
      html += `<br/>Tax Due: $${Number(tile.amount)}`;
    }

    if (tile.price) {
      const mortVal = Math.floor(Number(tile.price) / 2);
      const unmortCost = Math.floor(Number(tile.price) * 0.55);
      html += `<br/>Mortgage Value: $${mortVal} · Unmortgage: $${unmortCost}`;
    }

    propPanel.innerHTML = html;

    if (!isSpectator && ownerId === meId) {
      const sub = latestState.subphase;
      const isMyTurn = latestState.turn_player_id === meId && latestState.phase === 'playing';
      const inOwnDebt =
        sub === 'resolve_debt' &&
        latestState.phase === 'playing' &&
        latestState.pending_debt?.debtor_id === meId;
      const canManageProps =
        !mySt.bankrupt &&
        latestState.phase === 'playing' &&
        sub !== 'auction' &&
        (isMyTurn || inOwnDebt);

      const groupTiles = tile.kind === 'prop' ? board.filter((b) => b.group === tile.group) : [];
      const ownsGroup =
        tile.kind === 'prop' &&
        groupTiles.length > 0 &&
        groupTiles.every((b) => ownership[String(b.id)] === meId);
      const anyGroupMortgaged = groupTiles.some((b) => mortgaged.has(b.id));
      const anyGroupHouses = groupTiles.some((b) => (houses[String(b.id)] || 0) > 0);
      const minGroupH = groupTiles.length ? Math.min(...groupTiles.map((b) => houses[String(b.id)] || 0)) : 0;
      const maxGroupH = groupTiles.length ? Math.max(...groupTiles.map((b) => houses[String(b.id)] || 0)) : 0;

      const btnRow = document.createElement('div');
      btnRow.className = 'mono-prop-actions';
      if (tile.kind === 'prop') {
        const buildDisabled =
          !canManageProps ||
          !ownsGroup ||
          anyGroupMortgaged ||
          hCount >= 5 ||
          hCount > minGroupH ||
          (mySt.cash || 0) < (tile.house_cost || 0);
        const sellDisabled = !canManageProps || hCount <= 0 || hCount < maxGroupH;
        btnRow.append(
          makeSmallBtn('BUILD', () => sendAction('build_house', { tile_id: tile.id }), buildDisabled),
          makeSmallBtn('SELL HOUSE', () => sendAction('sell_house', { tile_id: tile.id }), sellDisabled)
        );
      }
      if (!isMort) {
        const mortDisabled = !canManageProps || anyGroupHouses;
        btnRow.appendChild(
          makeSmallBtn('MORTGAGE', () => sendAction('mortgage', { tile_id: tile.id }), mortDisabled)
        );
      } else {
        const unmortCost = Math.floor((tile.price || 0) * 0.55);
        const unmortDisabled = !canManageProps || (mySt.cash || 0) < unmortCost;
        btnRow.appendChild(
          makeSmallBtn('UNMORTGAGE', () => sendAction('unmortgage', { tile_id: tile.id }), unmortDisabled)
        );
      }
      propPanel.appendChild(btnRow);
    }
  }

  function ensureBoardBuilt(board) {
    if (boardBuilt) return;
    boardBuilt = true;
    boardEl.innerHTML = '';
    tileNodes.clear();

    board.forEach((tile) => {
      const pos = tileGridPos(tile.id);
      const cell = document.createElement('div');
      cell.className = `mono-tile ${tile.id % 10 === 0 ? 'corner' : ''}`;
      cell.style.gridRow = String(pos.row);
      cell.style.gridColumn = String(pos.col);

      if (tile.group && VALID_GROUPS.has(tile.group)) {
        const band = document.createElement('div');
        band.className = `mono-band mono-group-${tile.group}`;
        cell.appendChild(band);
      }

      const name = document.createElement('div');
      name.className = 'mono-tile-name';
      name.textContent = tile.name;
      cell.appendChild(name);

      let priceEl = null;
      if (tile.price) {
        priceEl = document.createElement('div');
        priceEl.className = 'mono-tile-price';
        cell.appendChild(priceEl);
      }

      const tokenRow = document.createElement('div');
      tokenRow.className = 'mono-tokens-row';
      cell.appendChild(tokenRow);

      cell.addEventListener('click', () => {
        sound.click();
        selectedTileId = tile.id;
        tileNodes.forEach((entry, id) => {
          entry.cell.classList.toggle('is-selected', id === selectedTileId);
        });
        const t = (latestState.board || [])[tile.id] || tile;
        renderInspector(t);
      });

      tileNodes.set(tile.id, {
        cell,
        priceEl,
        tokenRow,
        lastPriceClass: '',
        lastPriceText: '',
        lastTokensSig: '',
      });
      boardEl.appendChild(cell);
    });

    const center = document.createElement('div');
    center.className = 'mono-center';

    centerTitleEl = document.createElement('div');
    centerTitleEl.className = 'bunker-sublabel';
    centerNoteEl = document.createElement('div');
    centerNoteEl.className = 'clue-item mono-center-note hidden';
    centerActionsEl = document.createElement('div');
    centerActionsEl.className = 'mono-center-actions';

    center.append(centerTitleEl, centerNoteEl, centerActionsEl);
    boardEl.appendChild(center);
  }

  return {
    update(publicState, _privateState, players) {
      latestState = publicState || {};
      latestPlayers = players || getPlayers() || [];
      const board = latestState.board || [];
      if (!board.length) return;

      const meId = getPlayerId();
      const me = latestPlayers.find((p) => p.id === meId);
      const isSpectator = Boolean(!me || me.role === 'spectator');
      const activePlayers = getActivePlayers(latestPlayers);

      const pState = latestState.players_state || {};
      const ownership = latestState.ownership || {};
      const houses = latestState.houses || {};
      const mortgaged = new Set(latestState.mortgaged || []);
      const isMyTurn = !isSpectator && latestState.turn_player_id === meId && latestState.phase === 'playing';
      const sub = latestState.subphase;
      const mySt = pState[meId] || {};

      ensureBoardBuilt(board);

      // Incrementally patch only changed tiles
      board.forEach((tile) => {
        const entry = tileNodes.get(tile.id);
        if (!entry) return;
        entry.cell.classList.toggle('is-selected', selectedTileId === tile.id);

        if (entry.priceEl && tile.price) {
          const h = houses[String(tile.id)] || 0;
          const ownIdx = activePlayers.findIndex((p) => p.id === ownership[String(tile.id)]);
          const ownTag = ownIdx >= 0 ? `P${ownIdx + 1}` : `$${tile.price}`;
          const houseTag = h > 0 ? ` · ${h === 5 ? 'H' : h + 'h'}` : '';
          const nextPriceText = `${mortgaged.has(tile.id) ? 'MORT' : ownTag}${houseTag}`;
          const nextPriceClass = ownIdx >= 0 ? `mono-tile-price mono-player-${ownIdx % 6}` : 'mono-tile-price';
          if (entry.lastPriceText !== nextPriceText) {
            entry.lastPriceText = nextPriceText;
            entry.priceEl.textContent = nextPriceText;
          }
          if (entry.lastPriceClass !== nextPriceClass) {
            entry.lastPriceClass = nextPriceClass;
            entry.priceEl.className = nextPriceClass;
          }
        }

        const tokensSig = activePlayers
          .map((p, idx) => {
            const ps = pState[p.id];
            return ps && !ps.bankrupt && ps.pos === tile.id ? `${idx}:${p.id}` : '';
          })
          .filter(Boolean)
          .join(',');
        if (entry.lastTokensSig !== tokensSig) {
          entry.lastTokensSig = tokensSig;
          entry.tokenRow.innerHTML = '';
          activePlayers.forEach((p, idx) => {
            const ps = pState[p.id];
            if (ps && !ps.bankrupt && ps.pos === tile.id) {
              const pip = document.createElement('span');
              pip.className = `mono-token-pip mono-player-${idx % 6}`;
              pip.title = p.name;
              entry.tokenRow.appendChild(pip);
            }
          });
        }
      });

      // Center Dashboard incremental update
      const turnP = activePlayers.find((p) => p.id === latestState.turn_player_id);
      const diceTxt = (latestState.last_dice || []).length ? `[${latestState.last_dice.join(' + ')}]` : '—';
      centerTitleEl.textContent = `ACTIVE: ${turnP?.name || '—'} · DICE ${diceTxt}`;

      if (latestState.last_card_text) {
        centerNoteEl.classList.remove('hidden');
        centerNoteEl.textContent = latestState.last_card_text;
      } else {
        centerNoteEl.classList.add('hidden');
        centerNoteEl.textContent = '';
      }

      if (sub === 'auction' && latestState.auction) {
        const auc = latestState.auction;
        const bidder = activePlayers.find((p) => p.id === auc.highest_bidder);
        const modeKey = `auction:${auc.tile_id}`;
        if (lastCenterSig !== modeKey || !auctionTitleEl) {
          lastCenterSig = modeKey;
          lastAuctionBtnsSig = '';
          centerActionsEl.innerHTML = '';

          const box = document.createElement('div');
          box.className = 'mono-auction-box';
          auctionTitleEl = document.createElement('div');
          auctionTitleEl.className = 'mono-auction-title';
          auctionBidEl = document.createElement('div');
          auctionBidEl.className = 'mono-auction-bid';
          auctionBtnsEl = document.createElement('div');
          auctionBtnsEl.className = 'mono-auction-btns';
          box.append(auctionTitleEl, auctionBidEl, auctionBtnsEl);
          centerActionsEl.appendChild(box);
        }

        auctionTitleEl.textContent = `LIVE AUCTION: ${auc.tile_name} (${auc.time_remaining}s)`;
        auctionBidEl.textContent = `HIGH BID: $${Number(auc.highest_bid)} (${bidder?.name || 'NONE'})`;

        const canBid = !isSpectator && !mySt.bankrupt && !(auc.passed || []).includes(meId);
        const btnsSig = `${canBid}:${auc.highest_bid}:${mySt.cash ?? 0}`;
        if (lastAuctionBtnsSig !== btnsSig) {
          lastAuctionBtnsSig = btnsSig;
          auctionBtnsEl.innerHTML = '';
          if (canBid) {
            [10, 50, 100].forEach((inc) => {
              const amt = Number(auc.highest_bid) + inc;
              const b = makeSmallBtn(
                `+$${inc} ($${amt})`,
                () => sendAction('bid', { amount: amt }),
                (mySt.cash || 0) < amt
              );
              auctionBtnsEl.appendChild(b);
            });
            auctionBtnsEl.appendChild(makeSmallBtn('PASS', () => sendAction('pass_auction', {})));
          }
        }
      } else {
        auctionTitleEl = null;
        auctionBidEl = null;
        auctionBtnsEl = null;
        lastAuctionBtnsSig = '';

        const actionSig = `${latestState.phase}:${sub}:${isMyTurn}:${mySt.pos}:${mySt.cash}:${mySt.in_jail}:${mySt.goojf}:${latestState.pending_debt?.debtor_id}:${latestState.pending_debt?.amount}`;
        if (lastCenterSig !== actionSig) {
          lastCenterSig = actionSig;
          centerActionsEl.innerHTML = '';

          if (isMyTurn && sub === 'roll') {
            const rollBtn = document.createElement('button');
            rollBtn.type = 'button';
            rollBtn.className = 'pill-btn pill-btn-lg';
            rollBtn.textContent = 'ROLL 2D6';
            rollBtn.addEventListener('click', () => {
              sound.dice();
              sendAction('roll', {});
            });
            centerActionsEl.appendChild(rollBtn);

            if (mySt.in_jail) {
              centerActionsEl.appendChild(
                makeSmallBtn('PAY $50 BAIL', () => sendAction('pay_jail', {}), (mySt.cash || 0) < 50)
              );
              if (mySt.goojf > 0) {
                centerActionsEl.appendChild(makeSmallBtn('USE JAIL FREE CARD', () => sendAction('use_goojf', {})));
              }
            }
          } else if (isMyTurn && sub === 'buy_or_auction') {
            const tile = board[mySt.pos];
            const buyBtn = document.createElement('button');
            buyBtn.type = 'button';
            buyBtn.className = 'pill-btn pill-btn-md';
            buyBtn.textContent = `BUY ${tile?.name || ''} ($${tile?.price || 0})`;
            buyBtn.disabled = (mySt.cash || 0) < (tile?.price || 0);
            buyBtn.addEventListener('click', () => {
              sound.click();
              sendAction('buy', {});
            });
            const aucBtn = document.createElement('button');
            aucBtn.type = 'button';
            aucBtn.className = 'pill-btn pill-btn-md pill-btn-alarm';
            aucBtn.textContent = 'PASS → 15S AUCTION';
            aucBtn.addEventListener('click', () => {
              sound.skru();
              sendAction('pass_buy', {});
            });
            centerActionsEl.append(buyBtn, aucBtn);
          } else if (!isSpectator && sub === 'resolve_debt' && latestState.pending_debt?.debtor_id === meId) {
            const debt = latestState.pending_debt;
            const warn = document.createElement('div');
            warn.className = 'mono-debt-warn';
            warn.textContent = `DEBT DUE: $${Number(debt.amount)} (${debt.reason || ''}) — Liquidate properties then Pay Debt.`;
            centerActionsEl.appendChild(warn);
            centerActionsEl.appendChild(
              makeSmallBtn('PAY DEBT', () => sendAction('pay_debt', {}), (mySt.cash || 0) < (debt.amount || 0))
            );
            centerActionsEl.appendChild(makeSmallBtn('DECLARE BANKRUPT', () => sendAction('declare_bankrupt', {})));
          } else if (isMyTurn && sub === 'end_turn') {
            const endBtn = document.createElement('button');
            endBtn.type = 'button';
            endBtn.className = 'pill-btn pill-btn-md';
            endBtn.textContent = 'END TURN →';
            endBtn.addEventListener('click', () => {
              sound.click();
              sendAction('end_turn', {});
            });
            centerActionsEl.appendChild(endBtn);
          }
        }
      }

      // Trade button guard (exclude spectators, debt, auction, pending trade, bankrupt)
      const hasPartner = activePlayers.some((p) => p.id !== meId && !pState[p.id]?.bankrupt);
      openTradeBtn.classList.toggle('hidden', isSpectator);
      openTradeBtn.disabled =
        isSpectator ||
        latestState.phase !== 'playing' ||
        Boolean(mySt.bankrupt) ||
        sub === 'auction' ||
        sub === 'resolve_debt' ||
        Boolean(latestState.pending_trade) ||
        !hasPartner;

      // Players List (exclude spectators)
      playersEl.innerHTML = '';
      activePlayers.forEach((p, idx) => {
        const st = pState[p.id] || {};
        const card = document.createElement('div');
        card.className = `mono-player-card ${latestState.turn_player_id === p.id && latestState.phase === 'playing' ? 'active' : ''}`;
        const propCount = Object.values(ownership).filter((o) => o === p.id).length;
        card.innerHTML = `
          <div class="mono-player-head">
            <span class="mono-player-name mono-player-${idx % 6}">● ${escapeHtml(p.name)}</span>
            <span>${st.bankrupt ? 'BANKRUPT' : `$${Number(st.cash ?? 0)}`}</span>
          </div>
          <div class="mono-player-meta">
            Props: ${propCount} · Jail Cards: ${Number(st.goojf || 0)}${st.in_jail ? ' · IN JAIL' : ''}
          </div>
        `;
        playersEl.appendChild(card);
      });

      // Pending Trade Notification
      const pt = latestState.pending_trade;
      if (!isSpectator && pt && (pt.to_id === meId || pt.from_id === meId)) {
        const fromP = activePlayers.find((p) => p.id === pt.from_id);
        const toP = activePlayers.find((p) => p.id === pt.to_id);
        const offerNames = (pt.offer_props || []).map((id) => escapeHtml(board[id]?.name || `#${id}`)).join(', ') || 'None';
        const reqNames = (pt.request_props || []).map((id) => escapeHtml(board[id]?.name || `#${id}`)).join(', ') || 'None';
        tradeOfferEl.classList.remove('hidden');
        tradeOfferEl.innerHTML = `
          <strong>TRADE: ${escapeHtml(fromP?.name || 'Player')} → ${escapeHtml(toP?.name || 'Player')}</strong><br/>
          Offers: $${Number(pt.offer_cash || 0)} + [${offerNames}]<br/>
          Wants: $${Number(pt.request_cash || 0)} + [${reqNames}]
        `;
        const row = document.createElement('div');
        row.className = 'mono-trade-offer-actions';
        if (pt.to_id === meId) {
          row.append(
            makeSmallBtn('ACCEPT', () => sendAction('accept_trade', {})),
            makeSmallBtn('DECLINE', () => sendAction('reject_trade', {}))
          );
        } else {
          row.appendChild(makeSmallBtn('CANCEL', () => sendAction('reject_trade', {})));
        }
        tradeOfferEl.appendChild(row);
      } else {
        tradeOfferEl.classList.add('hidden');
      }

      if (selectedTileId !== null && board[selectedTileId]) {
        renderInspector(board[selectedTileId]);
      }
    },
    destroy() {
      openTradeBtn.removeEventListener('click', onOpenTrade);
      tradeCloseBtn.removeEventListener('click', onCloseTrade);
      tradePartnerSel.removeEventListener('change', onPartnerChange);
      tradeSendBtn.removeEventListener('click', onSendTrade);
      tileNodes.clear();
    },
  };
}
