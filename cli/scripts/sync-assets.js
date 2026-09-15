#!/usr/bin/env node
// scripts/sync-assets.js
// Copies skill files from project root into cli/assets/ so they get bundled
// with the npm package. Run before publishing: npm run sync-assets
//
// Usage:
//   node scripts/sync-assets.js          (from cli/ directory)
//   npm run sync-assets                  (same thing)

'use strict';

const fs   = require('fs');
const path = require('path');

// cli/ is our cwd; root is one level up
const CLI_DIR  = __dirname.endsWith('scripts')
  ? path.resolve(__dirname, '..')       // run from scripts/
  : __dirname;                          // run from cli/
const ROOT_DIR = path.resolve(CLI_DIR, '..');
const ASSETS   = path.resolve(CLI_DIR, 'assets');

// ── helpers ────────────────────────────────────────────────────────────────

function copyRecursive(src, dest, { exclude = [] } = {}) {
  if (!fs.existsSync(src)) {
    console.warn(`  ⚠️  Source not found, skipping: ${src}`);
    return 0;
  }
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    let count = 0;
    for (const entry of fs.readdirSync(src)) {
      if (exclude.includes(entry)) continue;
      count += copyRecursive(path.join(src, entry), path.join(dest, entry), { exclude });
    }
    return count;
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
    return 1;
  }
}

function cleanDir(dir) {
  if (fs.existsSync(dir)) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
  fs.mkdirSync(dir, { recursive: true });
}

// ── asset specs ────────────────────────────────────────────────────────────
// Each entry: { src (relative to root), dest (relative to cli/assets/) }

const ASSET_SPECS = [
  // Primary skill (shared by most platforms)
  {
    src:  '.agents/skills/paper-to-learning-path',
    dest: 'skill',
    exclude: ['__pycache__'],
  },
  // Claude-specific extras
  {
    src:  '.claude-plugin',
    dest: 'claude-plugin',
  },
  // Cursor rule
  {
    src:  '.cursor/rules/paper-to-learning-path.mdc',
    dest: 'cursor-rules/paper-to-learning-path.mdc',
  },
  // Root rule files
  { src: '.cursorrules',   dest: '.cursorrules' },
  { src: '.windsurfrules', dest: '.windsurfrules' },
  { src: '.clinerules',    dest: '.clinerules' },
  { src: 'CLAUDE.md',      dest: 'CLAUDE.md' },
];

// ── main ───────────────────────────────────────────────────────────────────

console.log('🌿 Syncing assets from project root → cli/assets/\n');
cleanDir(ASSETS);

let totalFiles = 0;
for (const spec of ASSET_SPECS) {
  const srcPath  = path.resolve(ROOT_DIR, spec.src);
  const destPath = path.resolve(ASSETS, spec.dest);
  const count    = copyRecursive(srcPath, destPath, { exclude: spec.exclude || [] });
  totalFiles += count;
  console.log(`  ✓  ${spec.src} → assets/${spec.dest}  (${count} file(s))`);
}

console.log(`\n✅ Done! ${totalFiles} file(s) synced to cli/assets/\n`);
