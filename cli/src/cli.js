// src/cli.js — p2lp CLI command handler

'use strict';

const path = require('path');
const { PLATFORMS, resolvePlatform, getAllPlatformKeys } = require('./platforms');
const { installFileSpec, uninstallFileSpec } = require('./installer');

const VERSION = require('../package.json').version;

// ── colour helpers (no deps) ───────────────────────────────────────────────
const c = {
  green:  (s) => `\x1b[32m${s}\x1b[0m`,
  yellow: (s) => `\x1b[33m${s}\x1b[0m`,
  cyan:   (s) => `\x1b[36m${s}\x1b[0m`,
  bold:   (s) => `\x1b[1m${s}\x1b[0m`,
  dim:    (s) => `\x1b[2m${s}\x1b[0m`,
  red:    (s) => `\x1b[31m${s}\x1b[0m`,
};

// ── simple arg parser ──────────────────────────────────────────────────────
function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('-')) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    } else {
      args._.push(a);
    }
  }
  return args;
}

// ── usage ──────────────────────────────────────────────────────────────────
function showHelp() {
  const platforms = getAllPlatformKeys().join(', ');
  console.log(`
${c.bold('p2lp')} — paper-to-learning-path installer  ${c.dim('v' + VERSION)}

${c.bold('Usage:')}
  p2lp init --ai <platform>           Install skill to current project
  p2lp init --ai <platform> --global  Install globally (all projects)
  p2lp init --ai all                  Install for all supported platforms
  p2lp uninstall [--ai <platform>]    Remove skill files
  p2lp update                         Re-copy files from installed package
  p2lp list                           Show supported platforms

${c.bold('Options:')}
  --ai <name>     Target AI assistant (see platforms below)
  --global        Install to global path (~/.claude/skills/, etc.)
  --dry-run       Preview actions without writing files
  --no-overwrite  Skip files that already exist

${c.bold('Platforms:')}
  ${platforms}
  all             Install for every supported assistant

${c.bold('Examples:')}
  p2lp init --ai antigravity
  p2lp init --ai claude --global
  p2lp init --ai cursor
  p2lp init --ai all
  p2lp uninstall --ai cursor
`);
}

function showList() {
  console.log(`\n${c.bold('Supported platforms:')}\n`);
  for (const [key, platform] of Object.entries(PLATFORMS)) {
    const aliases = platform.aliases.length
      ? c.dim(`  (aliases: ${platform.aliases.join(', ')})`)
      : '';
    console.log(`  ${c.cyan(key.padEnd(14))} ${platform.label}${aliases}`);
  }
  console.log();
}

// ── commands ───────────────────────────────────────────────────────────────
function cmdInit(args) {
  const aiArg   = args.ai;
  const isGlobal = args.global === true;
  const dryRun  = args['dry-run'] === true;
  const overwrite = args['no-overwrite'] !== true;

  if (!aiArg) {
    console.error(c.red('Error: --ai <platform> is required'));
    console.log('Run p2lp list to see available platforms, or use --ai all');
    process.exit(1);
  }

  // Resolve "all"
  const platformKeys = aiArg.toLowerCase() === 'all'
    ? getAllPlatformKeys()
    : (() => {
        const k = resolvePlatform(aiArg);
        if (!k) {
          console.error(c.red(`Error: Unknown platform "${aiArg}"`));
          console.log('Run p2lp list to see available platforms.');
          process.exit(1);
        }
        return [k];
      })();

  const targetRoot = process.cwd();

  for (const key of platformKeys) {
    const platform = PLATFORMS[key];

    // Determine target root for this platform
    let installRoot = targetRoot;
    if (isGlobal && platform.globalDir) {
      // For global installs, globalDir already points to the skill path —
      // set installRoot to parent so dest paths work correctly
      installRoot = path.dirname(platform.globalDir());
    }

    console.log(`\n${c.bold(c.green('→'))} Installing for ${c.bold(platform.label)}...`);
    if (dryRun) console.log(c.yellow('  (dry-run mode — no files will be written)'));

    let totalCopied = 0;
    for (const spec of platform.files) {
      const { copied } = installFileSpec(spec, installRoot, { overwrite, dryRun });
      totalCopied += copied;
    }

    if (!dryRun) {
      console.log(c.green(`  ✅ Done! ${totalCopied} file(s) installed.`));
      if (platform.note) console.log(c.dim(`  💡 ${platform.note}`));
    }
  }

  if (!dryRun) {
    console.log(`\n${c.bold('Next steps:')}`);
    console.log('  1. Make sure Python 3.9+ is installed: python --version');
    console.log('  2. Install dependencies: pip install pymupdf deep-translator langdetect');
    console.log('  3. Open your AI assistant and say:');
    console.log(c.cyan('     "Translate ./paper.pdf to Vietnamese with a full learning path."'));
    console.log();
  }
}

function cmdUninstall(args) {
  const aiArg  = args.ai;
  const dryRun = args['dry-run'] === true;

  const platformKeys = !aiArg
    ? getAllPlatformKeys()
    : aiArg.toLowerCase() === 'all'
      ? getAllPlatformKeys()
      : (() => {
          const k = resolvePlatform(aiArg);
          if (!k) {
            console.error(c.red(`Error: Unknown platform "${aiArg}"`));
            process.exit(1);
          }
          return [k];
        })();

  const targetRoot = process.cwd();

  for (const key of platformKeys) {
    const platform = PLATFORMS[key];
    console.log(`\n${c.bold(c.yellow('→'))} Uninstalling ${platform.label}...`);
    let anyRemoved = false;
    for (const spec of platform.files) {
      if (uninstallFileSpec(spec, targetRoot, { dryRun })) anyRemoved = true;
    }
    if (!anyRemoved) console.log(c.dim('  (nothing to remove)'));
  }
  console.log();
}

function cmdUpdate(args) {
  // Update = re-run init with overwrite for all platforms that are already installed
  const dryRun = args['dry-run'] === true;
  const targetRoot = process.cwd();
  const fs = require('fs');
  const path = require('path');

  let found = 0;
  for (const [key, platform] of Object.entries(PLATFORMS)) {
    // Check if first file dest exists
    const firstDest = path.resolve(targetRoot, platform.files[0].dest);
    if (fs.existsSync(firstDest)) {
      found++;
      console.log(`\n${c.bold(c.cyan('→'))} Updating ${platform.label}...`);
      for (const spec of platform.files) {
        installFileSpec(spec, targetRoot, { overwrite: true, dryRun });
      }
    }
  }

  if (found === 0) {
    console.log(c.yellow('\nNo installed platforms detected in current directory.'));
    console.log('Run p2lp init --ai <platform> to install first.\n');
  } else {
    console.log(c.green(`\n✅ Updated ${found} platform(s).\n`));
  }
}

// ── main ───────────────────────────────────────────────────────────────────
function run(argv) {
  const args = parseArgs(argv);
  const cmd  = args._[0];

  if (args.version || cmd === 'version') {
    console.log(`p2lp v${VERSION}`);
    return;
  }

  if (!cmd || args.help || cmd === 'help') {
    showHelp();
    return;
  }

  switch (cmd) {
    case 'init':      return cmdInit(args);
    case 'uninstall': return cmdUninstall(args);
    case 'update':    return cmdUpdate(args);
    case 'list':      return showList();
    default:
      console.error(c.red(`Unknown command: ${cmd}`));
      showHelp();
      process.exit(1);
  }
}

module.exports = { run };
