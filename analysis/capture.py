"""Capture Blackout Arcade screenshots + runtime metrics through Chrome DevTools Protocol."""

import asyncio
import base64
import json
import pathlib
import urllib.request

import websockets

OUT = pathlib.Path(__file__).resolve().parent / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "http://127.0.0.1:8123/"


async def main() -> None:
    targets = json.load(urllib.request.urlopen("http://127.0.0.1:9223/json/list"))
    page = next(t for t in targets if t["type"] == "page")
    ws = await websockets.connect(page["webSocketDebuggerUrl"], max_size=64 * 1024 * 1024)
    counter = 0

    async def call(method: str, params: dict | None = None) -> dict:
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

    async def js(expression: str):
        res = await call(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True, "awaitPromise": True},
        )
        return res.get("result", {}).get("value")

    async def shot(name: str) -> None:
        data = await call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
        (OUT / name).write_bytes(base64.b64decode(data["data"]))
        print("saved", name)

    await call("Page.enable")
    await call("Runtime.enable")
    await call("Emulation.setDeviceMetricsOverride", {
        "width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False,
    })
    await call("Page.navigate", {"url": BASE})
    await asyncio.sleep(3.0)
    await shot("01-entry-desktop.png")

    await js("localStorage.setItem('blackout_player_name','ANALYST'); sessionStorage.removeItem('blackout_client_id');")
    await call("Page.reload")
    await asyncio.sleep(3.0)
    await shot("02-lobby-desktop.png")

    print("lobby state:", await js("JSON.stringify({view: document.querySelector('#view-lobby').className, rail: document.querySelectorAll('.ps5-rail-tile').length, title: document.querySelector('#ps5-hero-title')?.textContent, stripHidden: document.querySelector('.ps5-bottom-strip-wrap')?.classList.contains('hidden')})"))

    await js("document.querySelector('[data-game-type=\"connect4\"]')?.click()")
    await asyncio.sleep(0.8)
    await shot("03-connect4-desktop.png")
    print("connect4:", await js("JSON.stringify({cards: document.querySelectorAll('.visual-activity-card').length, stripHidden: document.querySelector('.ps5-bottom-strip-wrap')?.classList.contains('hidden'), hero: document.querySelector('#ps5-hero-title')?.textContent, meta: document.querySelector('#ps5-hero-meta')?.textContent})"))

    await js("document.querySelector('[data-game-type=\"tic_tac_toe\"]')?.click()")
    await asyncio.sleep(0.8)
    await shot("04-tictactoe-desktop.png")
    print("ttt:", await js("JSON.stringify({cards: document.querySelectorAll('.visual-activity-card').length, stripHidden: document.querySelector('.ps5-bottom-strip-wrap')?.classList.contains('hidden'), hero: document.querySelector('#ps5-hero-title')?.textContent, meta: document.querySelector('#ps5-hero-meta')?.textContent})"))

    nav = await js("JSON.stringify(performance.getEntriesByType('navigation')[0])")
    print("navigation timing:", nav)
    res = await js("JSON.stringify(performance.getEntriesByType('resource').map(r=>({n:r.name.split('/').pop().split('?')[0], bytes:r.decodedBodySize, ms:Math.round(r.duration)})))")
    print("resources:", res)

    await call("Emulation.setDeviceMetricsOverride", {
        "width": 390, "height": 844, "deviceScaleFactor": 2, "mobile": True,
    })
    await call("Page.reload")
    await asyncio.sleep(3.0)
    await shot("05-lobby-mobile.png")
    print("mobile overflow:", await js("JSON.stringify({docW: document.documentElement.scrollWidth, winW: window.innerWidth, bodyOverflow: getComputedStyle(document.body).overflowX})"))

    await js("document.querySelector('[data-game-type=\"connect4\"]')?.click()")
    await asyncio.sleep(0.6)
    await shot("06-connect4-mobile.png")

    await ws.close()


asyncio.run(main())
