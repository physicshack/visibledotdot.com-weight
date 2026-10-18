#!/usr/bin/env python3
"""Headless browser checks for index.html. Firebase scripts and database hosts are BLOCKED, and the
Firebase load/sync paths are exercised against an in-page mock, so no live data is read or written.
Usage: python3 -m http.server 8202 &   then   python3 tests/browser_check.py http://localhost:8202/ [screens_dir]
Needs: pip install playwright (and a Chrome/Chromium; set CHROME=/path if not /usr/bin/google-chrome)."""
import json, sys, os, datetime
from playwright.sync_api import sync_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8202/'
OUT = sys.argv[2] if len(sys.argv) > 2 else None
CHROME = os.environ.get('CHROME', '/usr/bin/google-chrome')
NOW = datetime.datetime.fromisoformat('2026-10-18T21:00:00+01:00')
LEGACY_V3 = {'version': 3, 'weightData': [
    {'date': '2026-10-17', 'time': '07:10', 'stone': 14, 'lbs': 0, 'frac': 0.21, 'kg': 89.0},
    {'date': '2026-10-17', 'time': '21:30', 'stone': 13, 'lbs': 13, 'frac': 0.77, 'kg': 88.8},
    {'date': '2026-10-01', 'stone': 14, 'lbs': 2, 'frac': 0.4, 'kg': 90.0}],
  'journalData': [{'date': '2026-10-17', 'day': 'Sat', 'comment': 'old entry 17th', 'weight': 88.8, 'notes': 'n', 'checkin': {'omadKept': True, 'energy': 4}},
                  {'date': '2026-10-16', 'day': 'Fri', 'comment': 'old entry 16th', 'weight': None, 'notes': '',
                   'mealSnapshot': [{'key': 'POULTRY & MEATS-0', 'name': 'Chicken Breast (Med)', 'qty': 2}]}],
  'mealQtys': {}, 'chartRangeStart': 0, 'chartRangeEnd': 100}
LEGACY_FB = {'weightData': {'2026-10-17_0710': LEGACY_V3['weightData'][0], '2026-10-17_2130': LEGACY_V3['weightData'][1], '2026-10-01': LEGACY_V3['weightData'][2]},
             'journalData': {'2026-10-17': LEGACY_V3['journalData'][0], '2026-10-16': LEGACY_V3['journalData'][1]},
             'prefs': {'goalTarget': '85', 'currentUnit': 'kg'}}
R, FAILS = {}, []
def check(name, cond, detail=''):
    R[name] = 'PASS' if cond else f'FAIL {detail}'
    if not cond: FAILS.append(name)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
    ctx = b.new_context(viewport={'width': 1100, 'height': 1300}, has_touch=True, accept_downloads=True)
    for pat in ['**/*firebasedatabase.app/**', '**/*firebaseio.com/**', '**/firebasejs/**']:
        ctx.route(pat, lambda r: r.abort())
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept())
    pg.clock.install(time=NOW)
    pg.goto(URL); pg.wait_for_timeout(500); pg.clock.run_for(3000)  # let any start-up timers fire before seeding
    store = lambda: json.loads(pg.evaluate("()=>localStorage.getItem('weightTrackerData')"))

    # 1. migration of v3 localStorage
    pg.evaluate("s=>localStorage.setItem('weightTrackerData',s)", json.dumps(LEGACY_V3)); pg.reload(); pg.wait_for_timeout(1200)
    pg.evaluate("()=>persistAll()"); pg.wait_for_timeout(200)
    s = store()
    check('migrate: all v3 weight rows kept with ids', len(s['weightData']) == 3 and all(w.get('id') for w in s['weightData']), s['weightData'])
    check('migrate: all v3 journal rows kept with deterministic ids', sorted(j['id'] for j in s['journalData']) == ['j-2026-10-16-1', 'j-2026-10-17-1'], [j.get('id') for j in s['journalData']])
    check('migrate: content preserved', any(j['comment'] == 'old entry 17th' and j['weight'] == 88.8 and j['checkin']['energy'] == 4 for j in s['journalData']))
    check('migrate: export version 4', s.get('version') == 4)
    pg.reload(); pg.wait_for_timeout(1000)
    check('migrate: reload is stable (same ids)', sorted(j['id'] for j in store()['journalData']) == ['j-2026-10-16-1', 'j-2026-10-17-1'])

    # 2. journal: several entries on one day, edit one, delete one
    pg.click("nav button:has-text('Journal')"); pg.wait_for_timeout(300)
    for i, txt in enumerate(['Morning check-in', 'Lunch thought', 'Evening reflection', 'Late note']):
        pg.fill('#jDate', '2026-10-18'); pg.fill('#jComment', txt)
        if i == 0: pg.check('#jOmadKept')
        pg.click('#jSaveBtn'); pg.wait_for_timeout(150)
        pg.clock.run_for(60_000)
    pg.fill('#jDate', '2026-10-17'); pg.fill('#jComment', 'Back-dated second entry for the 17th'); pg.click('#jSaveBtn'); pg.wait_for_timeout(200)
    s = store(); day18 = [j for j in s['journalData'] if j['date'] == '2026-10-18']
    check('journal: 4 saves on one day = 4 records', len(day18) == 4, len(day18))
    check('journal: back-dated entry did not overwrite the 17th', len([j for j in s['journalData'] if j['date'] == '2026-10-17']) == 2)
    check('journal: ids unique', len({j['id'] for j in s['journalData']}) == len(s['journalData']))
    check('journal: list shows all 7', pg.locator('#journalList .journal-entry').count() == 7, pg.locator('#journalList .journal-entry').count())
    if OUT: pg.screenshot(path=f'{OUT}/after-journal-multi.png')
    # edit 'Lunch thought'
    pg.locator('#journalList .journal-entry', has_text='Lunch thought').click(); pg.wait_for_timeout(300)
    check('journal: edit banner + Update button', pg.is_visible('#jEditBanner') and pg.inner_text('#jSaveBtn') == 'Update Entry')
    pg.fill('#jComment', 'Lunch thought (edited)'); pg.click('#jSaveBtn'); pg.wait_for_timeout(200)
    s = store(); c18 = sorted(j['comment'] for j in s['journalData'] if j['date'] == '2026-10-18')
    check('journal: edit changed only that entry', c18 == ['Evening reflection', 'Late note', 'Lunch thought (edited)', 'Morning check-in'], c18)
    check('journal: after save form is back to new-entry mode', pg.inner_text('#jSaveBtn') == 'Save Entry')
    # delete 'Late note'
    btn = pg.locator('#journalList .journal-entry', has_text='Late note').locator('.delete-btn')
    btn.click(); btn.click(); pg.wait_for_timeout(200)
    c18 = sorted(j['comment'] for j in store()['journalData'] if j['date'] == '2026-10-18')
    check('journal: delete removed only that entry', c18 == ['Evening reflection', 'Lunch thought (edited)', 'Morning check-in'], c18)
    pg.click("nav button:has-text('Reset')"); pg.wait_for_timeout(300)
    check('reset: OMAD kept counted per day', '2/2' in pg.inner_text('#stateCheck'), pg.inner_text('#stateCheck'))

    # 3. OMAD: log to journal creates a NEW entry even while another was being edited; food delete works
    pg.click("nav button:has-text('Journal')"); pg.locator('#journalList .journal-entry', has_text='Morning').click(); pg.wait_for_timeout(200)
    pg.click("nav button:has-text('OMAD')"); pg.wait_for_timeout(200)
    pg.locator('.qty-stepper button', has_text='+').first.click(); pg.locator('.qty-stepper button', has_text='+').first.click()
    pg.click("button:has-text('Log to Journal')"); pg.wait_for_timeout(300)
    n_before = len(store()['journalData']); pg.click('#jSaveBtn'); pg.wait_for_timeout(200)
    s = store()
    check('omad: logged meal is a new entry (edit not hijacked)', len(s['journalData']) == n_before + 1 and any(j['comment'] == 'Morning check-in' for j in s['journalData']))
    pg.click("nav button:has-text('OMAD')"); pg.wait_for_timeout(200)
    check('omad: recent meal chip present', pg.locator('.meal-chip').count() >= 2, pg.locator('.meal-chip').count())
    pg.click("button:has-text('Edit Foods')"); n0 = pg.locator('#foodEditorBody tr').count()
    pg.locator('#fdel-0 .delete-btn').nth(1).click(); pg.locator('#fdel-0 button:has-text("Yes")').click(); pg.wait_for_timeout(200)
    check('food: delete works', pg.locator('#foodEditorBody tr').count() == n0 - 1)
    pg.click("button:has-text('Close')"); pg.wait_for_timeout(200)

    # 4. weight: add 2 readings today, delete one by id
    pg.click("nav button:has-text('Tracker')"); pg.wait_for_timeout(300)
    for st, lb in [(13, 13), (13, 12)]:
        pg.fill('#entryDate', '2026-10-18'); pg.fill('#entryStone', str(st)); pg.fill('#entryLbs', str(lb)); pg.dispatch_event('#entryLbs', 'input')
        pg.click("#entryRow button:has-text('Save')"); pg.wait_for_timeout(150); pg.clock.run_for(60_000)
    w18 = [w for w in store()['weightData'] if w['date'] == '2026-10-18']
    check('weight: 2 readings same day kept', len(w18) == 2, w18)
    check('weight: st/lb stored exactly (13st 13lb = 88.451 kg)', any(abs(w['kg'] - 88.451) < 0.001 and w['lbs'] == 13 and w['frac'] == 0 for w in w18), w18)
    pg.locator('#tableBody tr').first.locator('.delete-btn').click(); pg.locator('#tableBody tr').first.locator('.delete-btn', has_text='Yes').click(); pg.wait_for_timeout(200)
    check('weight: deleting one same-day reading keeps the other', len([w for w in store()['weightData'] if w['date'] == '2026-10-18']) == 1)

    # 5. sliders: keyboard + touch, displayed vs stored, persistence
    pg.focus('#rangeStart'); [pg.keyboard.press('ArrowRight') for _ in range(10)]; pg.clock.run_for(1000); pg.wait_for_timeout(200)
    st = store()
    check('slider: keyboard moves start by step 1 and persists', st['chartRangeStart'] == pg.evaluate("()=>+document.getElementById('rangeStart').value") and st['chartRangeUserSet'], (st['chartRangeStart'], pg.input_value('#rangeStart')))
    box = pg.locator('#rangeEnd').bounding_box(); pg.touchscreen.tap(box['x'] + box['width'] * 0.9, box['y'] + box['height'] / 2); pg.wait_for_timeout(200)
    tv = pg.evaluate("()=>[+document.getElementById('rangeEnd').value, chartRangeEnd]")
    check('slider: touch tap updates end; DOM == state', tv[0] == tv[1] and tv[0] < 100, tv)
    pg.focus('#rangeEnd'); pg.keyboard.press('End'); pg.clock.run_for(1000); pg.wait_for_timeout(100)
    pg.fill('#goalTarget', '85'); pg.dispatch_event('#goalTarget', 'input'); pg.clock.run_for(1000)
    pg.click(".unit-toggle button:has-text('KG')"); pg.wait_for_timeout(200)
    pg.reload(); pg.wait_for_timeout(1200); pg.click("nav button:has-text('Tracker')"); pg.wait_for_timeout(400)
    dom = pg.evaluate("()=>[+document.getElementById('rangeStart').value, +document.getElementById('rangeEnd').value, chartRangeStart, chartRangeEnd, document.getElementById('goalTarget').value, currentUnit, document.querySelector('.unit-toggle .active').textContent]")
    check('persist: slider DOM == stored state after reload', dom[0] == dom[2] and dom[1] == dom[3] == 100, dom)
    check('persist: goal target and unit survive reload', dom[4] == '85' and dom[5] == 'kg' and dom[6] == 'KG', dom)
    chart = pg.evaluate("""()=>{const c=Chart.getChart('weightChart');return {ds:c.data.datasets.map(d=>d.label), ymin:c.scales.y.min, ymax:c.scales.y.max,
       vals:c.data.datasets.flatMap(d=>d.data.map(p=>p.y)), xmin:c.scales.x.min, xmax:c.scales.x.max, xs:c.data.datasets.flatMap(d=>d.data.map(p=>p.x))}}""")
    check('chart: every plotted value inside the y axis', all(chart['ymin'] <= v <= chart['ymax'] for v in chart['vals']), chart)
    check('chart: every plotted x inside the x axis', all(chart['xmin'] <= x <= chart['xmax'] for x in chart['xs']))
    check('chart: projection drawn', 'Projection' in chart['ds'], chart['ds'])
    pg.clock.run_for(3000); pg.wait_for_timeout(300)  # let Chart.js animation finish under the fake clock
    if OUT: pg.locator('#weightChart').screenshot(path=f'{OUT}/after-chart-multi-kg.png')

    # 6. export → merge into itself adds nothing; legacy backup merge adds only what is missing
    with pg.expect_download() as dl: pg.click("header button:has-text('Export')")
    path = dl.value.path(); exported = json.load(open(path))
    before = (len(store()['weightData']), len(store()['journalData']))
    pg.set_input_files('#importFile', path); pg.wait_for_timeout(300); pg.click("#importModal button:has-text('Merge')"); pg.wait_for_timeout(300)
    check('import: merging own export adds nothing', (len(store()['weightData']), len(store()['journalData'])) == before)
    leg = '/tmp/legacy-backup.json'; L = json.loads(json.dumps(LEGACY_V3)); L['journalData'].append({'date': '2026-10-18', 'comment': 'from old backup'}); json.dump(L, open(leg, 'w'))
    pg.set_input_files('#importFile', leg); pg.wait_for_timeout(300); pg.click("#importModal button:has-text('Merge')"); pg.wait_for_timeout(300)
    check('import: legacy backup merge adds only the new record', len(store()['journalData']) == before[1] + 1, (before, len(store()['journalData'])))
    check('export: has ids on every record', all(r.get('id') for r in exported['weightData'] + exported['journalData']))

    # 7. Firebase paths against a MOCK (no network): legacy date-keyed data loads; writes are keyed by id
    res = pg.evaluate("""async (fb)=>{ let written=null;
        firebaseDB={ref:()=>({once:async()=>({val:()=>fb}), set:async(o)=>{written=o;}})}; fbUser='mock-user-not-live';
        const ok=await loadFromFirebase(); journalData.push({id:newId('j'),date:'2026-10-17',day:'Sat',comment:'2nd on 17th',weight:null,notes:''});
        syncToFirebase(); await new Promise(r=>setTimeout(r,0));
        const r={ok, jCount:journalData.length, keys:Object.keys(written.journalData), wkeys:Object.keys(written.weightData), goal:document.getElementById('goalTarget').value};
        firebaseDB=null; fbUser=''; return r;}""", LEGACY_FB)
    check('firebase(mock): legacy date-keyed journal loads', res['ok'] and res['jCount'] == 3, res)
    check('firebase(mock): write keyed by id, both 17 Oct entries kept', len(res['keys']) == 3 and all(k.startswith('j-') for k in res['keys']), res['keys'])
    check('no page errors', not errs, errs)
    b.close()
print(json.dumps(R, indent=1))
print(f"{len(R) - len(FAILS)}/{len(R)} browser checks passed")
sys.exit(1 if FAILS else 0)
