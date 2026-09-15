// src/installer.js — File copy/remove logic for p2lp

'use strict';

const fs   = require('fs');
const path = require('path');

const ASSETS_DIR = path.resolve(__dirname, '..', 'assets');

// ── helpers ────────────────────────────────────────────────────────────────

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const entry of fs.readdirSync(src)) {
      copyRecursive(path.join(src, entry), path.join(dest, entry));
    }
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
  }
}

function removeRecursive(target) {
  if (!fs.existsSync(target)) return false;
  const stat = fs.statSync(target);
  if (stat.isDirectory()) {
    for (const entry of fs.readdirSync(target)) {
      removeRecursive(path.join(target, entry));
    }
    fs.rmdirSync(target);
  } else {
    fs.unlinkSync(target);
  }
  return true;
}

function countFiles(dir) {
  if (!fs.existsSync(dir)) return 0;
  let count = 0;
  for (const entry of fs.readdirSync(dir)) {
    const full = path.join(dir, entry);
    if (fs.statSync(full).isDirectory()) {
      count += countFiles(full);
    } else {
      count++;
    }
  }
  return count;
}

// ── public API ─────────────────────────────────────────────────────────────

/**
 * Install one file spec ({ src, dest }) into targetRoot.
 * Returns { copied, skipped } file counts.
 */
function installFileSpec(spec, targetRoot, { overwrite = true, dryRun = false } = {}) {
  const srcPath  = path.resolve(ASSETS_DIR, spec.src);
  const destPath = path.resolve(targetRoot, spec.dest);

  if (!fs.existsSync(srcPath)) {
    console.warn(`  ⚠️  Asset not found: ${spec.src} (run "p2lp sync-assets" to rebuild)`);
    return { copied: 0, skipped: 0 };
  }

  if (!overwrite && fs.existsSync(destPath)) {
    return { copied: 0, skipped: 1 };
  }

  if (dryRun) {
    const n = fs.statSync(srcPath).isDirectory() ? countFiles(srcPath) : 1;
    console.log(`  [dry-run] Would copy ${spec.src} → ${path.relative(process.cwd(), destPath)}`);
    return { copied: n, skipped: 0 };
  }

  copyRecursive(srcPath, destPath);
  const n = fs.statSync(srcPath).isDirectory() ? countFiles(destPath) : 1;
  console.log(`  ✓  ${path.relative(process.cwd(), destPath)}`);
  return { copied: n, skipped: 0 };
}

/**
 * Uninstall one file spec from targetRoot.
 * Returns true if something was removed.
 */
function uninstallFileSpec(spec, targetRoot, { dryRun = false } = {}) {
  const destPath = path.resolve(targetRoot, spec.dest);
  if (dryRun) {
    console.log(`  [dry-run] Would remove ${path.relative(process.cwd(), destPath)}`);
    return true;
  }
  const removed = removeRecursive(destPath);
  if (removed) console.log(`  ✓  Removed ${path.relative(process.cwd(), destPath)}`);
  return removed;
}

module.exports = { installFileSpec, uninstallFileSpec };
