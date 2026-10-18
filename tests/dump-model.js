// Reads fixtures JSON on stdin, prints {trend, projection} per fixture as JSON. Used by independent_check.py.
const P = require('./load-pure').loadPure();
const fx = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = fx.map(f => {
  const t = P.computeTrend(f.weights);
  const latest = P.sortAsc(f.weights).at(-1);
  const p = P.projectGoal({ trend: t, latestKg: latest ? latest.kg : NaN, targetKg: f.target, todayStr: f.today });
  return { name: f.name, trend: t && { slopePerDay: t.slopePerDay, startKg: t.startKg, endKg: t.endKg, firstDate: t.firstDate, lastDate: t.lastDate },
    projection: { status: p.status, goalDate: p.goalDate || null, daysFromAnchor: p.daysFromAnchor ?? null } };
});
process.stdout.write(JSON.stringify(out));
