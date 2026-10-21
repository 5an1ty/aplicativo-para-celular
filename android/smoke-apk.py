#!/usr/bin/env python3
"""Exercise the actual APK's web assets in Chromium with external requests blocked.
This does not replace installing the native Android package on a device.
"""
import mimetypes
from pathlib import Path
from zipfile import ZipFile
from playwright.sync_api import sync_playwright

apk = Path(__file__).parent / 'build/Bob-Esponja-Snake.apk'
with ZipFile(apk) as z:
    assets = {n.removeprefix('assets/game/'): z.read(n) for n in z.namelist() if n.startswith('assets/game/')}
    assert z.read('classes.dex').startswith(b'dex\n')
assert b'fonts.googleapis.com' not in assets['style.css']
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width, height in [(390,844), (844,390), (360,640)]:
        context = browser.new_context(viewport={'width':width, 'height':height}, is_mobile=True, has_touch=True)
        errors = []
        def serve(route):
            prefix = 'https://game.local/'
            if not route.request.url.startswith(prefix):
                route.abort()
                return
            path = route.request.url.removeprefix(prefix) or 'index.html'
            if path not in assets:
                route.fulfill(status=404, body='')
                return
            mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
            route.fulfill(status=200, content_type=mime, body=assets[path])
        context.route('**/*', serve)
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto('https://game.local/')
        page.click('#startBtn')
        assert page.evaluate('paused')
        page.click('#resumeBtn')
        before = page.evaluate('gameTime')
        page.wait_for_timeout(450)
        assert page.evaluate('gameTime') > before
        page.evaluate("if(!paused)togglePause()")
        page.click('#menuBtn')
        page.click('[data-mode="battle"]')
        page.click('#startBtn')
        assert page.evaluate('playableTutorial !== null')
        assert page.locator('#trainingObjective').is_visible()
        # Lifecycle and native Back actions use these same JavaScript hooks.
        page.evaluate("if(!paused && !over)togglePause()")
        assert page.evaluate('paused')
        page.evaluate('goMenu()')
        assert page.locator('#menu').is_visible()
        # Media is bundled and decodable; no external network is used.
        assert page.evaluate("""async () => {
          const audio = new Audio('musicas/bgm_easy_explore.mp3');
          audio.muted = true;
          await audio.play();
          const ok = audio.readyState >= 2;
          audio.pause(); return ok;
        }""")
        assert not errors, errors
        print(f'PASS {width}x{height}: offline assets, movement, pause, menu, battle tutorial, audio')
        context.close()
    browser.close()
