#!/usr/bin/env python3
"""Responsive UI and existing game-rule checks. Serve ../megabrain on port 8010 first."""
from pathlib import Path
from playwright.sync_api import sync_playwright

screenshots = Path('/workspace/shared/mobile-redesign')
screenshots.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width, height in [(390,844),(360,640),(320,568),(412,915),(844,390),(1280,900)]:
        page = browser.new_page(viewport={'width':width,'height':height}, is_mobile=width<1000, has_touch=width<1000)
        page.set_default_timeout(10000)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto('http://127.0.0.1:8010/', wait_until='domcontentloaded')
        page.evaluate('document.fonts.ready')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        if width == 390:
            page.screenshot(path=str(screenshots/'menu.png'), full_page=True)
        page.click('.character[data-character="patrick"]')
        page.click('.difficulty[data-difficulty="medium"]')
        page.click('#startBtn')
        assert page.evaluate("character === 'patrick' && difficulty === 'medium' && gameMode === 'classic'")
        if page.evaluate('paused'):
            page.click('#resumeBtn')
        before = page.evaluate('gameTime')
        page.wait_for_timeout(250)
        assert page.evaluate('gameTime') > before
        page.click('#pauseBtn')
        assert page.evaluate('paused')
        assert page.locator('#overlay').is_visible()
        assert page.locator('.score-medal small').inner_text() == 'Pontos'
        # Existing food score multiplier and timed power behavior are unchanged.
        assert page.evaluate("""() => {
          const before = score;
          food = {x:4,y:4,type:'normal',id:++foodSerial}; collectFood();
          const scoreOK = score === before + 20;
          food = {x:4,y:4,type:'ghost',id:++foodSerial}; collectFood();
          return scoreOK && hasPower('ghost');
        }""")
        frozen = page.evaluate('gameTime')
        page.wait_for_timeout(100)
        assert page.evaluate('gameTime') == frozen
        # Real/fallback fullscreen must preserve the map aspect ratio and input separation.
        page.click('#pauseFullscreenBtn')
        page.wait_for_timeout(100)
        board = page.locator('#board').bounding_box()
        pad = page.locator('.touch-controls').bounding_box()
        ratio = page.evaluate('COLS/ROWS')
        assert abs(board['width']/board['height']-ratio) < .02
        assert board['x'] >= -1 and board['x']+board['width'] <= width+1
        assert board['y']+board['height'] <= height
        assert pad['x'] >= -1 and pad['x']+pad['width'] <= width+1
        assert pad['y']+pad['height'] <= height+1
        assert board['x']+board['width'] <= pad['x'] or board['y']+board['height'] <= pad['y']
        page.click('#menuBtn')
        assert page.locator('#menu').is_visible()
        assert not page.evaluate('document.body.classList.contains("playing")')
        page.click('.character[data-character="bob"]')
        page.click('[data-mode="battle"]')
        assert page.locator('.character[data-character="sandy"]').is_visible()
        page.click('#startBtn')
        assert page.evaluate('playableTutorial !== null')
        assert page.locator('#trainingObjective').is_visible()
        assert page.locator('.score-medal small').inner_text() == 'Pontos'
        if not page.evaluate('paused'):
            page.click('#pauseBtn')
        page.click('#menuBtn')
        page.click('.character[data-character="sandy"]')
        page.click('[data-mode="classic"]')
        assert page.evaluate("character === 'bob'")
        assert not page.locator('.character[data-character="sandy"]').is_visible()
        # Tutorial completion state exposes real Battle character abilities as before.
        page.evaluate("localStorage.setItem('bobSnakeBattlePlayableTutorialSeen','true')")
        page.click('[data-mode="battle"]')
        page.click('.character[data-character="sandy"]')
        page.click('#startBtn')
        assert page.evaluate("gameMode === 'battle' && character === 'sandy' && playableTutorial === null")
        assert page.locator('#abilityBtn').is_visible()
        page.click('#resumeBtn') if page.evaluate('paused') else None
        page.click('#abilityBtn')
        assert page.evaluate('karateArmed')
        page.click('#pauseBtn')
        page.click('#menuBtn')
        assert not errors, (width, errors)
        if width == 390:
            page.click('[data-mode="classic"]')
            page.click('.difficulty[data-difficulty="easy"]')
            page.click('#startBtn')
            page.click('#resumeBtn')
            page.wait_for_timeout(150)
            page.click('#pauseBtn')
            page.locator('#overlay').evaluate("el=>el.style.visibility='hidden'")
            page.screenshot(path=str(screenshots/'game.png'))
        print(f'PASS {width}x{height}: layout, fullscreen, movement, food score, powers, pause, tutorial, Battle ability', flush=True)
        page.close()
    browser.close()
