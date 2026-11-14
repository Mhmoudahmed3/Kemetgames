"""Drive a real solo-vs-AI match in Chrome and capture the arena."""

import asyncio
import base64
import json
import pathlib
import urllib.request

import websockets

OUT = pathlib.Path(__file__).resolve().parent / "screenshots"


async def main() -> None:
    targets = json.load(urllib.request.urlopen("http://127.0.0.1:9223/json/list"))
    page = next(t for t in targets if t["type"] == "page")
    ws = await websockets.connect(page["webSocketDebuggerUrl"], max_size=64 * 1024 * 1024)
    counter = 0

    async def call(method, params=None):
        nonlocal counter
        counter += 1
        mid = counter
        await ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    async def js(expression):
        res = await call("Runtime.evaluate", {"expression": expression, "returnByValue": True, "awaitPromise": True})
        return res.get("result", {}).get("value")

    async def shot(name):
        data = await call("Page.captureScreenshot", {"format": "png"})
        (OUT / name).write_bytes(base64.b64decode(data["data"]))
        print("saved", name)

    await call("Page.enable")
    await call("Runtime.enable")
    await call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False})
    await call("Page.navigate", {"url": "http://127.0.0.1:8123/"})
    await asyncio.sleep(2.5)
    await js("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(String(e.message))); window.addEventListener('unhandledrejection',e=>window.__errs.push(String(e.reason)));")
    await js("localStorage.setItem('blackout_player_name','ANALYST')")
    await call("Page.reload")
    await asyncio.sleep(2.5)

    # Connect 4 vs AI
    await js("document.querySelector('[data-game-type=\"connect4\"]')?.click()")
    await asyncio.sleep(0.5)
    await js("document.querySelector('#btn-matchup-ai')?.click()")
    await asyncio.sleep(0.4)
    print("launch label:", await js("document.querySelector('#btn-pregame-launch')?.textContent"))
    await js("document.querySelector('#btn-pregame-launch')?.click()")
    await asyncio.sleep(2.5)
    await shot("07-connect4-arena.png")
    print("arena:", await js("JSON.stringify({arenaHidden: document.querySelector('#view-arena')?.classList.contains('hidden'), room: document.querySelector('#hud-room-code')?.textContent, turn: document.querySelector('#hud-turn-indicator')?.textContent, discs: document.querySelectorAll('.c4-disc').length, errs: window.__errs})"))

    # Click a column to drop a disc
    clicked = await js("(()=>{const b=document.querySelector('.c4-drop-btn, .c4-col-drop, [data-col]'); if(!b) return 'none'; b.click(); return b.className})()")
    print("clicked column control:", clicked)
    await asyncio.sleep(1.5)
    await shot("08-connect4-after-move.png")
    print("after move:", await js("JSON.stringify({turn: document.querySelector('#hud-turn-indicator')?.textContent, discs: document.querySelectorAll('.c4-disc').length, events: [...document.querySelectorAll('#arena-events-list .log-entry')].map(e=>e.textContent).slice(-3), errs: window.__errs})"))

    # Tic tac toe solo
    await js("document.querySelector('#btn-leave-room, [id*=leave]')?.click()")
    await asyncio.sleep(0.8)
    await js("document.querySelector('[data-game-type=\"tic_tac_toe\"]')?.click()")
    await asyncio.sleep(0.5)
    await js("document.querySelector('#btn-matchup-ai')?.click()")
    await asyncio.sleep(0.3)
    await js("document.querySelector('#btn-pregame-launch')?.click()")
    await asyncio.sleep(2.0)
    await shot("09-tictactoe-arena.png")
    print("ttt arena:", await js("JSON.stringify({room: document.querySelector('#hud-room-code')?.textContent, cells: document.querySelectorAll('.ttt-cell').length, errs: window.__errs})"))

    await ws.close()


asyncio.run(main())
