#!/usr/bin/env node
/**
 * fix-mermaid-unicode.js — Replace characters that Mermaid 9.4.3's flowchart
 * lexer rejects inside node/subgraph labels, but ONLY within ```mermaid fenced
 * blocks (prose text — including em-dashes — is left untouched).
 *
 * Usage: node fix-mermaid-unicode.js <file.md> [file.md ...]
 */
const fs = require('fs');

const REPLACEMENTS = [
  [/\u2014/g, '-'],   // — em dash
  [/\u2013/g, '-'],   // – en dash
  [/\u2192/g, '->'],  // → right arrow
  [/\u2194/g, '<->'], // ↔ left-right arrow
  [/\u2212/g, '-'],   // − minus sign
  [/\u00d7/g, 'x'],   // × multiplication
  [/\u00b1/g, '+/-'], // ± plus-minus
  [/\u2022/g, '-'],   // • bullet
  [/\u2264/g, '<='],  // ≤
  [/\u2265/g, '>='],  // ≥
  [/~(?=\d)/g, ''],   // ~ before a digit (e.g. ~125ms) — tilde breaks the lexer
];

function fixBlock(block) {
  let out = block;
  for (const [re, to] of REPLACEMENTS) out = out.replace(re, to);
  return out;
}

let total = 0;
for (const file of process.argv.slice(2)) {
  const md = fs.readFileSync(file, 'utf8');
  let count = 0;
  const fixed = md.replace(/```mermaid\s*\n[\s\S]*?```/g, (block) => {
    const nb = fixBlock(block);
    if (nb !== block) count += 1;
    return nb;
  });
  if (fixed !== md) {
    fs.writeFileSync(file, fixed);
    console.log(`fixed ${count} block(s) in ${file}`);
    total += count;
  } else {
    console.log(`no change  ${file}`);
  }
}
console.log(`\nDone. ${total} block(s) updated.`);
