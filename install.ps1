<#
.SYNOPSIS
    Installs paper-to-learning-path skill on Windows for Antigravity, Claude Code, and Cursor.
.EXAMPLE
    .\install.ps1
#>

Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  📄  paper-to-learning-path — Skill Installer (PowerShell)       ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# 1. Install python packages
Write-Host "==> Installing Python dependencies..." -ForegroundColor Cyan
python -m pip install --quiet --upgrade pymupdf deep-translator langdetect

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillSrc = Join-Path $ScriptDir ".agents\skills\paper-to-learning-path"
$HomeDir = [System.Environment]::GetFolderPath('UserProfile')

# 2. Antigravity Global
$AntigravityDir = Join-Path $HomeDir ".gemini\antigravity\skills\paper-to-learning-path"
try {
    if (Test-Path (Join-Path $HomeDir ".gemini")) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $AntigravityDir) | Out-Null
        if (Test-Path $AntigravityDir) { Remove-Item -Recurse -Force $AntigravityDir }
        Copy-Item -Recurse -Force $SkillSrc $AntigravityDir
        Write-Host "  [OK] Antigravity skill installed: $AntigravityDir" -ForegroundColor Green
    }
} catch {
    Write-Host "  [SKIP] Antigravity directory: $_" -ForegroundColor Yellow
}

# 3. Claude Code Global
$ClaudeDir = Join-Path $HomeDir ".claude\skills\paper-to-learning-path"
try {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ClaudeDir) | Out-Null
    if (Test-Path $ClaudeDir) { Remove-Item -Recurse -Force $ClaudeDir }
    Copy-Item -Recurse -Force $SkillSrc $ClaudeDir
    Write-Host "  [OK] Claude Code skill installed: $ClaudeDir" -ForegroundColor Green
} catch {
    Write-Host "  [SKIP] Claude Code directory: $_" -ForegroundColor Yellow
}

# 4. Cursor Rule Global
$CursorRuleSrc = Join-Path $ScriptDir ".cursor\rules\paper-to-learning-path.mdc"
$CursorDir = Join-Path $HomeDir ".cursor\rules"
try {
    if (Test-Path $CursorRuleSrc) {
        New-Item -ItemType Directory -Force -Path $CursorDir | Out-Null
        Copy-Item -Force $CursorRuleSrc (Join-Path $CursorDir "paper-to-learning-path.mdc")
        Write-Host "  [OK] Cursor rule installed: $(Join-Path $CursorDir 'paper-to-learning-path.mdc')" -ForegroundColor Green
    }
} catch {
    Write-Host "  [SKIP] Cursor directory: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete! You can now use the skill in your AI agent." -ForegroundColor Green
Write-Host "Prompt example: 'Convert paper.pdf to Vietnamese with a complete learning path'" -ForegroundColor Yellow
Write-Host ""
