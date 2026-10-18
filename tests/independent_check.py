#!/usr/bin/env python3
"""Independent check of the trend + projection maths in index.html using numpy.polyfit.
Usage: python3 tests/independent_check.py   (needs numpy and node)"""
import json, subprocess, datetime as dt, math, random, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
D0 = dt.date(1970, 1, 1)
def dnum(s): return (dt.date.fromisoformat(s) - D0).days
def dstr(n): return (D0 + dt.timedelta(days=n)).isoformat()

def expected(f):
    by = {}
    for w in f['weights']: by.setdefault(w['date'], []).append(w['kg'])
    days = sorted(by)
    if len(days) < 2: return None, {'status': 'no-trend'}
    x = np.array([dnum(d) for d in days], float); y = np.array([np.mean(by[d]) for d in days])
    b, a = np.polyfit(x - x[0], y, 1)
    trend = dict(slopePerDay=b, startKg=a, endKg=a + b * (x[-1] - x[0]), firstDate=days[0], lastDate=days[-1])
    latest = sorted(f['weights'], key=lambda w: (w['date'], w.get('time', '')))[-1]['kg']
    T = f['target']
    if latest <= T: return trend, {'status': 'reached'}
    if b * 7 > -0.005: return trend, {'status': 'not-losing'}
    if trend['endKg'] <= T: return trend, {'status': 'trend-at-target'}
    k = (T - trend['endKg']) / b
    if k > 730: return trend, {'status': 'too-far'}
    goal = dstr(dnum(days[-1]) + math.ceil(k - 1e-9))
    return trend, {'status': 'past' if goal < f['today'] else 'ok', 'goalDate': goal, 'daysFromAnchor': k}

def W(d, kg, t=None):
    r = {'date': d, 'kg': kg}
    if t: r['time'] = t
    return r
fixtures = [
  {'name': 'seed-uneven', 'today': '2026-10-18', 'target': 85, 'weights': [W('2026-09-01',92.0),W('2026-09-02',91.8),W('2026-09-03',91.9),W('2026-09-04',91.5),W('2026-09-05',91.6),W('2026-09-20',90.6),W('2026-10-05',89.9),W('2026-10-17',89.0,'07:10'),W('2026-10-17',88.8,'21:30')]},
  {'name': 'embedded-2026', 'today': '2026-10-18', 'target': 74.3, 'weights': [W(d,k) for d,k in [('2026-02-11',105.682),('2026-03-12',97.971),('2026-03-13',96.157),('2026-03-17',95.590),('2026-03-20',95.137),('2026-03-28',91.848),('2026-03-30',94.003),('2026-03-31',92.642),('2026-04-01',92.642),('2026-04-03',92.302),('2026-04-07',93.096),('2026-04-09',91.735),('2026-04-16',90.828),('2026-04-20',90.107),('2026-04-21',89.916),('2026-04-24',89.354),('2026-04-27',88.138)]]},
  {'name': 'across-dst', 'today': '2026-10-30', 'target': 88, 'weights': [W('2026-10-20',90.4),W('2026-10-24',90.1,'07:00'),W('2026-10-25',90.0,'01:30'),W('2026-10-25',89.9,'01:10'),W('2026-10-26',89.7),W('2026-10-29',89.5)]},
  {'name': 'flat', 'today': '2026-10-18', 'target': 80, 'weights': [W('2026-10-01',90),W('2026-10-09',90),W('2026-10-17',90)]},
  {'name': 'one-day', 'today': '2026-10-18', 'target': 80, 'weights': [W('2026-10-17',90,'07:00'),W('2026-10-17',89.6,'20:00')]},
]
rng = random.Random(42)
for i in range(40):
    start = dnum('2026-01-01') + rng.randint(0, 200); ws = []; d = start; kg = rng.uniform(80, 110); rate = rng.uniform(-0.15, 0.03)
    for _ in range(rng.randint(2, 40)):
        d += rng.choice([0, 1, 1, 2, 3, 7, 14]); kg += rate * 1 + rng.gauss(0, 0.4)
        ws.append(W(dstr(d), round(kg, 2), f"{rng.randint(5,22):02d}:{rng.randint(0,59):02d}"))
    fixtures.append({'name': f'random-{i}', 'today': dstr(d + rng.randint(-5, 60)), 'target': round(kg - rng.uniform(-2, 15), 1), 'weights': ws})

js = json.loads(subprocess.run(['node', os.path.join(HERE, 'dump-model.js')], input=json.dumps(fixtures), capture_output=True, text=True, check=True).stdout)
bad = 0; statuses = {}
for f, got in zip(fixtures, js):
    et, ep = expected(f)
    errs = []
    if (et is None) != (got['trend'] is None): errs.append('trend presence')
    elif et:
        for k in ('slopePerDay', 'startKg', 'endKg'):
            if abs(et[k] - got['trend'][k]) > 1e-8: errs.append(f"{k} {et[k]} vs {got['trend'][k]}")
    if ep['status'] != got['projection']['status']: errs.append(f"status {ep['status']} vs {got['projection']['status']}")
    elif 'goalDate' in ep:
        if ep['goalDate'] != got['projection']['goalDate']: errs.append(f"goalDate {ep['goalDate']} vs {got['projection']['goalDate']}")
        if abs(ep['daysFromAnchor'] - got['projection']['daysFromAnchor']) > 1e-6: errs.append('daysFromAnchor')
    statuses[ep['status']] = statuses.get(ep['status'], 0) + 1
    if errs: bad += 1; print('MISMATCH', f['name'], errs)
    elif f['name'] in ('seed-uneven', 'embedded-2026', 'across-dst'):
        print(f"{f['name']}: slope {got['trend']['slopePerDay']*7:+.4f} kg/wk, end-fit {got['trend']['endKg']:.3f} kg, projection {got['projection']}")
print(f"{len(fixtures)-bad}/{len(fixtures)} fixtures match numpy (tolerance 1e-8); statuses covered: {statuses}")
sys.exit(1 if bad else 0)
