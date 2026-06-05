#!/usr/bin/env node
/**
 * md2pdf.js — Convert Markdown files (including Mermaid diagrams) to PDF.
 *
 * This script and its dependencies live in `node-module/` (a sibling of the
 * docs folder). The Markdown directory is provided via the MD2PDF_DOCS_DIR
 * environment variable (set by generate-pdf.sh); it falls back to the current
 * working directory. Each PDF is written next to its source. Prefer invoking
 * this through `generate-pdf.sh`.
 *
 * Usage:
 *   node md2pdf.js                     Convert every .md file in the docs folder
 *   node md2pdf.js a.md b.md           Convert only the named files (docs folder)
 *   npm run pdf                        Same as `node md2pdf.js`
 *
 * Setup (one time):
 *   npm install
 *
 * How it works:
 *   1. `marked` turns Markdown into HTML; ```mermaid fences become
 *      <pre class="mermaid"> blocks.
 *   2. Puppeteer (headless Chromium) loads the HTML, injects the locally
 *      bundled mermaid.js, and renders every diagram to SVG offline.
 *   3. The page is printed to <name>.pdf next to the source file.
 *
 * No network access is required — mermaid is loaded from node_modules.
 */

const fs = require('fs');
const path = require('path');
const { marked } = require('marked');
const puppeteer = require('puppeteer');

const MERMAID_JS = require.resolve('mermaid/dist/mermaid.min.js');

const PAGE_CSS = `
  body {
    font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 12px; line-height: 1.55; color: #1f2328;
    max-width: 900px; margin: 0 auto; padding: 8px 4px;
  }
  h1 { font-size: 22px; border-bottom: 2px solid #d0d7de; padding-bottom: 6px; }
  h2 { font-size: 17px; border-bottom: 1px solid #d8dee4; padding-bottom: 4px; margin-top: 22px; }
  h3 { font-size: 14px; margin-top: 16px; }
  table { border-collapse: collapse; width: 100%; margin: 10px 0; }
  th, td { border: 1px solid #d0d7de; padding: 5px 9px; text-align: left; vertical-align: top; }
  th { background: #f6f8fa; }
  pre { background: #f6f8fa; padding: 12px; border-radius: 6px; overflow: auto; }
  code { font-family: SFMono-Regular, Consolas, "Liberation Mono", monospace; font-size: 11px; }
  pre code { background: none; padding: 0; }
  blockquote { color: #57606a; border-left: 4px solid #d0d7de; margin: 10px 0; padding: 2px 14px; }
  pre.mermaid { background: none; border: 0; padding: 0; text-align: center; }
  pre.mermaid svg { max-width: 100%; height: auto; }
  /* Never split a diagram or table across a page break. */
  pre.mermaid, table { break-inside: avoid; page-break-inside: avoid; }
`;

const PDF_OPTIONS = {
  format: 'A4',
  printBackground: true,
  margin: { top: '18mm', bottom: '18mm', left: '14mm', right: '14mm' },
};

const MERMAID_CONFIG = {
  startOnLoad: false,
  securityLevel: 'loose', // allow <br/> in node labels
  theme: 'default',
  flowchart: { htmlLabels: true, useMaxWidth: true },
  sequence: { useMaxWidth: true },
};

function escapeHtml(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Render ```mermaid fences as <pre class="mermaid">; fall back to the default
// renderer for every other code block (returning false tells marked to do so).
marked.use({
  renderer: {
    code(code, infostring) {
      const lang = (infostring || '').trim().split(/\s+/)[0];
      if (lang === 'mermaid') {
        return `<pre class="mermaid">${escapeHtml(code)}</pre>`;
      }
      return false;
    },
  },
});

function buildHtml(markdown) {
  const body = marked.parse(markdown);
  return `<!doctype html>
<html><head><meta charset="utf-8"><style>${PAGE_CSS}</style></head>
<body>${body}</body></html>`;
}

function resolveTargets() {
  // Docs dir is passed by generate-pdf.sh; fall back to the current directory.
  const docsDir = process.env.MD2PDF_DOCS_DIR
    ? path.resolve(process.env.MD2PDF_DOCS_DIR)
    : process.cwd();
  const args = process.argv.slice(2);
  const names = args.length > 0 ? args : fs.readdirSync(docsDir).filter((f) => f.toLowerCase().endsWith('.md'));
  return names.map((n) => (path.isAbsolute(n) ? n : path.resolve(docsDir, n)));
}

async function convertOne(browser, input) {
  const output = input.replace(/\.md$/i, '.pdf');
  const markdown = fs.readFileSync(input, 'utf8');
  const page = await browser.newPage();
  try {
    await page.setContent(buildHtml(markdown), { waitUntil: 'load' });
    await page.addScriptTag({ path: MERMAID_JS });
    await page.evaluate(async (config) => {
      const m = window.mermaid;
      m.initialize(config);
      if (typeof m.run === 'function') {
        await m.run({ querySelector: 'pre.mermaid' });
      } else {
        m.init(undefined, document.querySelectorAll('pre.mermaid'));
      }
    }, MERMAID_CONFIG);
    await page.pdf({ path: output, ...PDF_OPTIONS });
  } finally {
    await page.close();
  }
  return output;
}

async function main() {
  const targets = resolveTargets();
  if (targets.length === 0) {
    console.error('No .md files found to convert.');
    process.exit(1);
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  let failures = 0;
  try {
    for (const input of targets) {
      const name = path.basename(input);
      if (!fs.existsSync(input)) {
        console.warn(`  skip   ${name} (not found)`);
        failures += 1;
        continue;
      }
      process.stdout.write(`  build  ${name} ... `);
      try {
        const output = await convertOne(browser, input);
        console.log(`ok -> ${path.basename(output)}`);
      } catch (err) {
        failures += 1;
        console.log('FAILED');
        console.error(`         ${err && err.message ? err.message : err}`);
      }
    }
  } finally {
    await browser.close();
  }

  console.log(`\nDone. ${targets.length - failures}/${targets.length} converted.`);
  process.exit(failures > 0 ? 1 : 0);
}

main();
