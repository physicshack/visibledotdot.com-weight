#!/usr/bin/env node
// Unit tests for the maths / dates / entries / trend / projection helpers in index.html.
// Usage: node tests/run-tests.js            (runs the suite in Europe/London, UTC and America/Los_Angeles)
//        TZ=Europe/London node tests/run-tests.js --single
const { spawnSync } = require('child_process');
if (!process.argv.includes('--single')) {
  let failed = 0;
  for (const tz of ['Europe/London', 'UTC', 'America/Los_Angeles']) {
    const r = spawnSync(process.execPath, [__filename, '--single'], { env: { ...process.env, TZ: tz }, stdio: 'inherit' });
    if (r.status !== 0) failed++;
  }
  process.exit(failed ? 1 : 0);
}

const P = require('./load-pure').loadPure();
let pass = 0, fail = 0;
const failures = [];
function test(name, fn) {
  try { fn(); pass++; } catch (e) { fail++; failures.push(`  ✗ ${name}\n      ${e.message}`); }
}
function eq(a, b, msg) { if (a !== b) throw new Error(`${msg || ''} expected ${JSON.stringify(b)}, got ${JSON.stringify(a)}`); }
function near(a, b, tol, msg) { if (!(Math.abs(a - b) <= tol)) throw new Error(`${msg || ''} expected ${b} ± ${tol}, got ${a}`); }
function ok(c, msg) { if (!c) throw new Error(msg || 'assertion failed'); }

const W = (date, kg, time, extra) => ({ date, kg, ...(time ? { time } : {}), ...(extra || {}) });

// ── Units ──────────────────────────────────────────────────────────────
test('kg→st/lb: 95.25 kg is 15st 0.0lb (old code showed "14st 14.0lb")', () => {
  eq(P.fmtStone(95.25), '15st 0.0lb');
});
test('kg→st/lb: 88.138 kg = 194.31 lb = 13st 12.3lb', () => {
  const r = P.kgToStLbs(88.138, 2); eq(r.stone, 13); near(r.lbs, 12.31, 0.005);
  eq(P.fmtStone(88.138), '13st 12.3lb');
});
test('st/lb→kg exact: 14st 3lb = 199 lb = 90.26488 kg', () => near(P.stLbsToKg(14, 3), 90.26488163, 1e-6));
test('round trip st/lb → kg → st/lb is stable for every whole lb 8st..25st', () => {
  for (let lb = 112; lb <= 350; lb++) {
    const st = Math.floor(lb / 14), l = lb % 14;
    eq(P.fmtStone(P.stLbsToKg(st, l)), `${st}st ${l.toFixed(1)}lb`, `${st}st ${l}lb`);
  }
});
test('stoneFields never produces lbs=14 or frac=1.00', () => {
  for (let kg = 50; kg < 130; kg += 0.0137) {
    const f = P.stoneFields(kg);
    ok(f.lbs >= 0 && f.lbs <= 13 && f.frac >= 0 && f.frac < 1, `${kg}: ${JSON.stringify(f)}`);
    near((f.stone * 14 + f.lbs + f.frac) * P.KG_PER_LB, kg, 0.0024, `kg ${kg}`);
  }
});
test('1 stone = 6.35029318 kg', () => near(P.KG_PER_STONE, 6.35029318, 1e-8));
test('fmtStoneTick: 13.5 st → "13st 7lb", 14 st → "14st 0lb"', () => { eq(P.fmtStoneTick(13.5), '13st 7lb'); eq(P.fmtStoneTick(14), '14st 0lb'); });

// ── BMI ───────────────────────────────────────────────────────────────
const H = (5 * 12 + 8) * 0.0254; // 1.7272 m
test('BMI 88.138 kg @ 1.7272 m = 29.545', () => near(P.bmiFor(88.138, H), 29.5446, 1e-3));
test('BMI goal weight 24.9 × h² = 74.28 kg', () => near(24.9 * H * H, 74.282, 1e-3));
test('BMI label matches the displayed 1-dp value (24.96 shows "25.0" → Overweight)', () => {
  eq(P.bmiStatus(24.96).label, 'Overweight'); eq(P.bmiStatus(24.94).label, 'Healthy');
  eq(P.bmiStatus(29.96).label, 'Obese'); eq(P.bmiStatus(18.44).label, 'Underweight');
});

// ── Dates / DST ───────────────────────────────────────────────────────
test('daysBetween across the 25 Oct 2026 clock change is exactly 1/2 days', () => {
  eq(P.daysBetween('2026-10-24', '2026-10-25'), 1); eq(P.daysBetween('2026-10-24', '2026-10-26'), 2);
  eq(P.daysBetween('2026-03-28', '2026-03-30'), 2); // spring forward
});
test('addDaysStr over DST and year end', () => { eq(P.addDaysStr('2026-10-24', 2), '2026-10-26'); eq(P.addDaysStr('2026-12-31', 1), '2027-01-01'); eq(P.addDaysStr('2026-10-18', -29), '2026-09-19'); });
test('dayName is zone-independent', () => { eq(P.dayName('2026-10-25'), 'Sun'); eq(P.dayName('2026-02-11'), 'Wed'); });
test('localDateStr uses LOCAL date (00:30 BST on 19 Oct is the 19th, not UTC 18th)', () => {
  const d = new Date(2026, 9, 19, 0, 30); eq(P.localDateStr(d), '2026-10-19');
});
test('ordering: 21:30 reading is after 07:10 the same day; legacy (no time) first', () => {
  const s = P.sortAsc([W('2026-10-17', 88.8, '21:30', { id: 'b' }), W('2026-10-17', 89.0, '07:10', { id: 'a' }), W('2026-10-17', 89.5, null, { id: 'c' })]);
  eq(s.map(x => x.id).join(), 'c,a,b');
});
test('ordering: DST repeated hour 01:30 BST then 01:10 GMT on 25 Oct sorted by real timestamp', () => {
  const bst = { id: 'x', date: '2026-10-25', time: '01:30', ts: Date.UTC(2026, 9, 25, 0, 30), kg: 1 };
  const gmt = { id: 'y', date: '2026-10-25', time: '01:10', ts: Date.UTC(2026, 9, 25, 1, 10), kg: 1 };
  eq(P.sortAsc([gmt, bst]).map(x => x.id).join(), 'x,y');
});

// ── Migration ─────────────────────────────────────────────────────────
test('journal migration: legacy date-keyed Firebase object loads losslessly with deterministic ids', () => {
  const fb = { '2026-04-27': { date: '2026-04-27', day: 'Mon', comment: 'A', weight: 88.1, notes: '' }, '2026-04-28': { date: '2026-04-28', comment: '', weight: null } };
  const j = P.normalizeJournalEntries(fb);
  eq(j.length, 2); eq(j[0].id, 'j-2026-04-27-1'); eq(j[0].comment, 'A'); eq(j[0].weight, 88.1); eq(j[1].day, 'Tue');
  eq(JSON.stringify(P.normalizeJournalEntries(fb)), JSON.stringify(j), 'deterministic');
});
test('journal migration: legacy array with two same-date rows keeps both (ids -1, -2)', () => {
  const j = P.normalizeJournalEntries([{ date: '2026-10-18', comment: 'a' }, { date: '2026-10-18', comment: 'b' }]);
  eq(j.map(x => x.id).join(), 'j-2026-10-18-1,j-2026-10-18-2');
});
test('journal migration: existing ids kept; junk rows dropped; weight "" → null', () => {
  const j = P.normalizeJournalEntries([{ id: 'j-abc', date: '2026-10-18', comment: 'x', weight: '' }, null, { date: 'bad' }, 'str']);
  eq(j.length, 1); eq(j[0].id, 'j-abc'); eq(j[0].weight, null);
});
test('weight migration: legacy rows get ids, stone fields filled when missing, Firebase object ok', () => {
  const w = P.normalizeWeightEntries({ '2026-10-17_0710': { date: '2026-10-17', time: '07:10', kg: 89 }, '2026-10-16': { date: '2026-10-16', kg: '90.5', stone: 14, lbs: 3, frac: 0.5 } });
  eq(w.length, 2); eq(w[0].id, 'w-2026-10-17-0710-1'); eq(w[0].stone, 14); eq(w[1].kg, 90.5); eq(w[1].id, 'w-2026-10-16-na-1');
});
test('merge is lossless: same id+content skipped, same id+different content kept under new id', () => {
  const a = P.normalizeJournalEntries([{ date: '2026-10-18', comment: 'mine' }]);
  const b = P.normalizeJournalEntries([{ date: '2026-10-18', comment: 'mine' }, { date: '2026-10-18', comment: 'second' }]);
  const c = P.normalizeJournalEntries([{ date: '2026-10-18', comment: 'edited elsewhere' }]);
  let r = P.mergeEntries(a, b, 'journal'); eq(r.added, 1); eq(r.list.length, 2);
  r = P.mergeEntries(r.list, c, 'journal'); eq(r.added, 1); eq(r.list.length, 3);
  eq(new Set(r.list.map(x => x.id)).size, 3, 'ids unique');
  r = P.mergeEntries(r.list, r.list, 'journal'); eq(r.added, 0, 'idempotent');
});
test('Firebase keyed object uses ids, so 3 entries on one date stay 3', () => {
  const j = P.normalizeJournalEntries([{ date: '2026-10-18', comment: '1' }, { date: '2026-10-18', comment: '2' }, { id: 'j-a.b', date: '2026-10-18', comment: '3' }]);
  const o = P.toKeyedObject(j); eq(Object.keys(o).length, 3); ok(o['j-a_b'], 'unsafe "." replaced');
  eq(P.normalizeJournalEntries(o).length, 3, 'round trip');
});

// ── Trend (verified independently with numpy.polyfit in tests/independent_check.py) ──
const SEED = [W('2026-09-01', 92.0), W('2026-09-02', 91.8), W('2026-09-03', 91.9), W('2026-09-04', 91.5), W('2026-09-05', 91.6),
  W('2026-09-20', 90.6), W('2026-10-05', 89.9), W('2026-10-17', 89.0, '07:10'), W('2026-10-17', 88.8, '21:30')];
test('trend: OLS on daily means vs real days — numpy slope −0.0632842 kg/day (−0.44299 kg/wk)', () => {
  const t = P.computeTrend(SEED);
  near(t.slopePerDay, -0.06328416461, 1e-9); near(t.kgPerWeek, -0.44298915227, 1e-9);
  near(t.startKg, 91.88724674281, 1e-8); near(t.endKg, 88.97617517075, 1e-8);
  eq(t.days.length, 8); near(t.days[7].kg, 88.9, 1e-12);
});
test('trend edge cases: 0 points, 1 point, all on one day → null (no rate)', () => {
  eq(P.computeTrend([]), null); eq(P.computeTrend([W('2026-10-01', 90)]), null);
  eq(P.computeTrend([W('2026-10-01', 90, '07:00'), W('2026-10-01', 89, '20:00')]), null);
});
test('trend: perfectly linear data recovers the exact slope regardless of uneven spacing', () => {
  const pts = [0, 1, 2, 10, 30, 31, 90].map(d => W(P.addDaysStr('2026-01-01', d), 100 - 0.1 * d));
  const t = P.computeTrend(pts); near(t.slopePerDay, -0.1, 1e-12); near(t.endKg, 91, 1e-9);
});

// ── Projection ────────────────────────────────────────────────────────
test('projection: continues the trend from its end point; numpy crossing 2026-12-18 19:56 → goal 19 Dec', () => {
  const t = P.computeTrend(SEED);
  const p = P.projectGoal({ trend: t, latestKg: 88.8, targetKg: 85, todayStr: '2026-10-18' });
  eq(p.status, 'ok'); eq(p.anchor.date, '2026-10-17'); near(p.anchor.kg, 88.97617517, 1e-6);
  near(p.daysFromAnchor, 62.830, 1e-3); eq(p.goalDate, '2026-12-19'); eq(p.daysFromToday, 62);
  near(p.anchor.kg + t.slopePerDay * p.daysFromAnchor, 85, 1e-9, 'line meets target');
});
test('projection: flat trend → not-losing (no date, no line)', () => {
  const t = P.computeTrend([W('2026-10-01', 90), W('2026-10-08', 90), W('2026-10-15', 90)]);
  eq(P.projectGoal({ trend: t, latestKg: 90, targetKg: 80, todayStr: '2026-10-18' }).status, 'not-losing');
});
test('projection: gaining → not-losing', () => {
  const t = P.computeTrend([W('2026-10-01', 90), W('2026-10-15', 91)]);
  eq(P.projectGoal({ trend: t, latestKg: 91, targetKg: 80, todayStr: '2026-10-18' }).status, 'not-losing');
});
test('projection: goal already reached', () => {
  const t = P.computeTrend(SEED);
  eq(P.projectGoal({ trend: t, latestKg: 84.9, targetKg: 85, todayStr: '2026-10-18' }).status, 'reached');
});
test('projection: 0/1 points → no-trend; no target → no-target', () => {
  eq(P.projectGoal({ trend: null, latestKg: 90, targetKg: 80, todayStr: '2026-10-18' }).status, 'no-trend');
  eq(P.projectGoal({ trend: null, latestKg: 90, targetKg: NaN, todayStr: '2026-10-18' }).status, 'no-target');
});
test('projection: stale data whose crossing is before today → status past (not presented as future)', () => {
  const pts = [W('2026-03-01', 100), W('2026-03-15', 98), W('2026-04-01', 96)];
  const p = P.projectGoal({ trend: P.computeTrend(pts), latestKg: 96, targetKg: 90, todayStr: '2026-10-18' });
  eq(p.status, 'past'); ok(p.goalDate < '2026-10-18', p.goalDate); ok(p.daysFromToday < 0);
});
test('projection: very slow loss (>2 years) → too-far, axis not stretched', () => {
  const pts = [W('2026-10-01', 90), W('2026-10-15', 89.98)];
  eq(P.projectGoal({ trend: P.computeTrend(pts), latestKg: 89.98, targetKg: 80, todayStr: '2026-10-18' }).status, 'too-far');
});
test('projection: trend line already below target while latest reading is above → trend-at-target', () => {
  const pts = [W('2026-10-01', 90), W('2026-10-02', 80), W('2026-10-03', 85.2)];
  eq(P.projectGoal({ trend: P.computeTrend(pts), latestKg: 85.2, targetKg: 85, todayStr: '2026-10-18' }).status, 'trend-at-target');
});
test('progressPct: 105.68 → 88.14 with target 74.3 = 55.9%; clamped 0..100', () => {
  near(P.progressPct(105.682, 88.138, 74.3), 55.905, 0.001);
  eq(P.progressPct(90, 95, 80), 0); eq(P.progressPct(90, 70, 80), 100); eq(P.progressPct(80, 85, 90), null);
});

// ── Stats ─────────────────────────────────────────────────────────────
test('summary: latest is the 21:30 reading; since last = −0.2 kg (old code said +0.2)', () => {
  const s = P.weightSummary(SEED, { todayStr: '2026-10-18' });
  eq(s.latest.kg, 88.8); near(s.change, -0.2, 1e-9);
});
test('summary: last 30 days = 19 Sep..18 Oct inclusive → 4 readings, 90.6 → 88.8 = −1.8 kg', () => {
  const s = P.weightSummary(SEED, { todayStr: '2026-10-18' });
  eq(s.recent.from, '2026-09-19'); eq(s.recent.count, 4); near(s.recent.change, -1.8, 1e-9);
});
test('summary: baseline = first reading on/after BASELINE_FROM, or true start when set', () => {
  const data = [W('2008-01-01', 95.25), W('2026-02-11', 105.682), W('2026-04-27', 88.138)];
  near(P.weightSummary(data, { baselineFrom: '2026-01-01', todayStr: '2026-10-18' }).totalLost, 17.544, 1e-9);
  near(P.weightSummary(data, { trueStartKg: 110, baselineFrom: '2026-01-01', todayStr: '2026-10-18' }).totalLost, 21.862, 1e-9);
  eq(P.weightSummary([], { todayStr: '2026-10-18' }), null);
});
test('state check counts DAYS, not entries (3 entries on one day = 1 OMAD day)', () => {
  const j = [{ date: '2026-10-18', checkin: { omadKept: true, energy: 4 } }, { date: '2026-10-18', checkin: { omadKept: false, energy: 2 } },
    { date: '2026-10-18', checkin: { alcohol: true } }, { date: '2026-10-17', checkin: { omadKept: true, energy: 3 } }, { date: '2026-10-16', comment: 'no checkin' }];
  const s = P.stateCheck(j, 14);
  eq(s.days, 2); eq(s.omadDays, 2); eq(s.alcoholDays, 1); near(s.energy, 3, 1e-12);
});

// ── Chart helpers ─────────────────────────────────────────────────────
test('rangeIndices: clamps, never inverted, works for n=1', () => {
  eq(JSON.stringify(P.rangeIndices(1, 0, 100)), '{"si":0,"ei":0}');
  eq(JSON.stringify(P.rangeIndices(43, 30, 80)), '{"si":13,"ei":34}');
  eq(JSON.stringify(P.rangeIndices(10, 90, 10)), '{"si":8,"ei":8}');
  eq(P.rangeIndices(0, 0, 100), null);
});
test('yAxisFor: covers all values with padding, whole-unit ticks (kg and stone)', () => {
  const vals = [85, 88.8, 92.0, 91.887];
  const k = P.yAxisFor(vals, 'kg'); ok(k.min < 85 && k.max > 92, JSON.stringify(k)); eq(k.min % k.stepSize, 0); eq(k.max % k.stepSize, 0);
  const s = P.yAxisFor(vals, 'stone'); ok(s.min * P.KG_PER_STONE < 85 && s.max * P.KG_PER_STONE > 92, JSON.stringify(s));
  near((s.min * 14) % 1, 0, 1e-9, 'whole lb'); near(Math.round(s.stepSize * 14), s.stepSize * 14, 1e-9);
  const flat = P.yAxisFor([90, 90], 'kg'); ok(flat.max > flat.min, 'flat data still has a range');
});

console.log(`[${process.env.TZ}] ${pass} passed, ${fail} failed`);
if (fail) { console.log(failures.join('\n')); process.exit(1); }
