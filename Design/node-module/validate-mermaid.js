#!/usr/bin/env node
/**
 * validate-mermaid.js — Parse every ```mermaid block in the design docs with the
 * bundled mermaid (same version md2pdf uses) and report syntax errors with the
 * file, block number, and the offending diagram text.
 *
 * Usage: node validate-mermaid.js [file.md ...]   (defaults to ../*\/*.md)
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');
const MERMAID_JS = require.resolve('mermaid/dist/mermaid.min.js');

function findDocs() {
  const args = process.argv.slice(2);
  if (args.length) return args.map((a) => path.resolve(a));
  const root = path.resolve(__dirname, '..');
  const out = [];
  for (const dir of fs.readdirSync(root)) {
    const full = path.join(root, dir);
    if (!fs.statSync(full).isDirectory() || dir === 'node-module') continue;
    for (const f of fs.readdirSync(full)) {
      if (f.toLowerCase().endsWith('.md')) out.push(path.join(full, f));
    }
  }
  return out;
}

function extractBlocks(md) {
  const blocks = [];
  const re = /```mermaid\s*\n([\s\S]*?)```/g;
  let m;
  let idx = 0;
  while ((m = re.exec(md)) !== null) {
    idx += 1;
    // 1-based starting line number of the diagram body
    const line = md.slice(0, m.index).split('\n').length;
    blocks.push({ num: idx, line, code: m[1] });
  }
  return blocks;
}

async function main() {
  const docs = findDocs();
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setContent('<!doctype html><html><body></body></html>', { waitUntil: 'load' });
  await page.addScriptTag({ path: MERMAID_JS });
  await page.evaluate(() => window.mermaid.initialize({ startOnLoad: false, securityLevel: 'loose' }));

  let failures = 0;
  for (const doc of docs) {
    const md = fs.readFileSync(doc, 'utf8');
    const blocks = extractBlocks(md);
    for (const b of blocks) {
      const result = await page.evaluate(async (code) => {
        try {
          await window.mermaid.parse(code);
          return { ok: true };
        } catch (e) {
          return { ok: false, msg: (e && e.message ? e.message : String(e)) };
        }
      }, b.code);
      if (!result.ok) {
        failures += 1;
        const firstLine = result.msg.split('\n')[0];
        console.log(`FAIL  ${path.relative(path.resolve(__dirname, '..'), doc)}  block #${b.num} (md line ~${b.line})`);
        console.log(`      ${firstLine}`);
        const lm = firstLine.match(/line (\d+)/);
        if (lm) {
          const n = parseInt(lm[1], 10);
          const diagLines = b.code.split('\n');
          const offending = diagLines[n - 1];
          if (offending !== undefined) console.log(`      >>> ${offending.trim()}`);
        }
      }
    }
  }
  await browser.close();
  console.log(`\n${failures === 0 ? 'All diagrams parsed OK.' : failures + ' diagram(s) failed.'}`);
  process.exit(failures > 0 ? 1 : 0);
}

main();
