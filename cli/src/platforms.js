// src/platforms.js — Platform definitions for p2lp installer

'use strict';

/**
 * Each platform entry defines:
 *   label      — human-readable name
 *   aliases    — alternative names accepted by --ai flag
 *   files      — list of { src, dest } copy operations
 *                src is relative to cli/assets/
 *                dest is relative to the target project root (or global dir)
 */

const PLATFORMS = {
  antigravity: {
    label: 'Google Antigravity',
    aliases: ['agy'],
    files: [
      { src: 'skill', dest: '.agents/skills/paper-to-learning-path' },
    ],
    globalDir: () => {
      const home = process.env.HOME || process.env.USERPROFILE || '';
      const isWin = process.platform === 'win32';
      return isWin
        ? `${home}\\.gemini\\antigravity\\skills\\paper-to-learning-path`
        : `${home}/.gemini/antigravity/skills/paper-to-learning-path`;
    },
    note: 'Skill auto-activates when you mention PDFs or research papers in Antigravity.',
  },

  claude: {
    label: 'Anthropic Claude Code',
    aliases: ['claude-code'],
    files: [
      { src: 'skill',         dest: '.claude/skills/paper-to-learning-path' },
      { src: 'claude-plugin', dest: '.claude-plugin' },
      { src: 'CLAUDE.md',     dest: 'CLAUDE.md' },
    ],
    globalDir: () => {
      const home = process.env.HOME || process.env.USERPROFILE || '';
      return `${home}/.claude/skills/paper-to-learning-path`;
    },
    note: 'Use /add-dir .claude/skills/paper-to-learning-path to register in Claude Code.',
  },

  cursor: {
    label: 'Cursor IDE',
    aliases: [],
    files: [
      { src: 'skill',                            dest: '.agents/skills/paper-to-learning-path' },
      { src: 'cursor-rules/paper-to-learning-path.mdc', dest: '.cursor/rules/paper-to-learning-path.mdc' },
      { src: '.cursorrules',                     dest: '.cursorrules' },
    ],
    note: 'Cursor auto-activates the rule for PDF translation requests.',
  },

  windsurf: {
    label: 'Windsurf (Cascade)',
    aliases: [],
    files: [
      { src: 'skill',        dest: '.agents/skills/paper-to-learning-path' },
      { src: '.windsurfrules', dest: '.windsurfrules' },
    ],
    note: 'Prompt Cascade: "Use paper-to-learning-path to translate ./paper.pdf"',
  },

  cline: {
    label: 'Cline',
    aliases: ['roocode', 'roo-code'],
    files: [
      { src: 'skill',      dest: '.agents/skills/paper-to-learning-path' },
      { src: '.clinerules', dest: '.clinerules' },
    ],
    note: 'Works with both Cline and Roo Code.',
  },

  aider: {
    label: 'Aider',
    aliases: [],
    files: [
      { src: 'skill', dest: '.agents/skills/paper-to-learning-path' },
    ],
    note: 'Run: aider --read .agents/skills/paper-to-learning-path/SKILL.md',
  },

  universal: {
    label: 'Universal (.agents/skills/)',
    aliases: ['agent-standard', 'agents'],
    files: [
      { src: 'skill', dest: '.agents/skills/paper-to-learning-path' },
    ],
    note: 'Standard .agents/skills/ path — works with any agent that supports this convention.',
  },
};

// Build reverse alias map for lookup
const ALIAS_MAP = {};
for (const [key, platform] of Object.entries(PLATFORMS)) {
  ALIAS_MAP[key] = key;
  for (const alias of platform.aliases || []) {
    ALIAS_MAP[alias] = key;
  }
}

function resolvePlatform(name) {
  if (!name) return null;
  return ALIAS_MAP[name.toLowerCase()] || null;
}

function getAllPlatformKeys() {
  return Object.keys(PLATFORMS);
}

module.exports = { PLATFORMS, resolvePlatform, getAllPlatformKeys };
