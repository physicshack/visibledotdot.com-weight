// Loads the @pure block out of ../index.html into a sandbox and returns its functions.
// No dependencies: node tests/run-tests.js
const fs = require('fs');
const path = require('path');
const vm = require('vm');

function loadPure() {
  const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
  const m = html.match(/\/\* @pure-begin \*\/([\s\S]*?)\/\* @pure-end \*\//);
  if (!m) throw new Error('@pure block not found in index.html');
  const names = [...m[1].matchAll(/^(?:function|const)\s+([A-Za-z_$][\w$]*)/gm)].map(x => x[1]);
  const sandbox = { crypto: globalThis.crypto, console };
  vm.createContext(sandbox);
  vm.runInContext(m[1] + `\n;globalThis.__pure = {${names.join(',')}};`, sandbox);
  return sandbox.__pure;
}
module.exports = { loadPure };
