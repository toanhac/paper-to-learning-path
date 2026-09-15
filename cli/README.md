# paper-to-learning-path-cli

> CLI installer for the [paper-to-learning-path](https://github.com/ToanHac/paper-to-learning-path) AI skill.

## Installation

```bash
npm install -g paper-to-learning-path-cli
```

## Usage

```bash
# Go to your project
cd /path/to/your/project

# Install for your AI assistant
p2lp init --ai antigravity   # Google Antigravity
p2lp init --ai claude        # Claude Code
p2lp init --ai cursor        # Cursor IDE
p2lp init --ai windsurf      # Windsurf (Cascade)
p2lp init --ai cline         # Cline / Roo Code
p2lp init --ai aider         # Aider
p2lp init --ai universal     # Universal (.agents/skills/)
p2lp init --ai all           # All platforms at once
```

## Other Commands

```bash
p2lp init --ai claude --global   # Install globally
p2lp init --ai cursor --dry-run  # Preview without writing
p2lp update                      # Refresh from installed package
p2lp uninstall --ai claude       # Remove for specific platform
p2lp list                        # Show all platforms
p2lp --help                      # Show full help
```

## Requirements

Python 3.9+ must be installed separately:

```bash
pip install pymupdf deep-translator langdetect
```
