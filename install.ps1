# ============================================================
# Antigravity Skills Installer
# Usage: irm https://raw.githubusercontent.com/josephithomas/jit/main/install.ps1 | iex
# ============================================================

$ErrorActionPreference = "Stop"
$globalSkillsDir = "$env:USERPROFILE\.gemini\config\skills"

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Antigravity Skills Installer" -ForegroundColor Cyan
Write-Host "  github.com/josephithomas/jit" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Ensure global skills directory exists
New-Item -ItemType Directory -Force -Path $globalSkillsDir | Out-Null

# -------------------------------------------------------
# STEP 1: Install custom skills from this repo
# -------------------------------------------------------
Write-Host "[1/2] Installing custom skills from josephithomas/jit..." -ForegroundColor Yellow

$customSkillsUrl = "https://api.github.com/repos/josephithomas/jit/contents/skills"
try {
    $skillFolders = Invoke-RestMethod -Uri $customSkillsUrl -UseBasicParsing
    foreach ($folder in $skillFolders) {
        if ($folder.type -eq "dir") {
            $skillName = $folder.name
            $destDir = Join-Path $globalSkillsDir $skillName
            New-Item -ItemType Directory -Force -Path $destDir | Out-Null

            $skillFileUrl = "https://raw.githubusercontent.com/josephithomas/jit/main/skills/$skillName/SKILL.md"
            try {
                Invoke-WebRequest -Uri $skillFileUrl -OutFile (Join-Path $destDir "SKILL.md") -UseBasicParsing
                Write-Host "  [+] $skillName" -ForegroundColor Green
            } catch {
                Write-Host "  [!] Failed to download $skillName/SKILL.md" -ForegroundColor Red
            }
        }
    }
} catch {
    Write-Host "  [!] Could not list skills from repo: $_" -ForegroundColor Red
}

# -------------------------------------------------------
# STEP 2: Install Awesome-Grok-Skills (518 skills)
# -------------------------------------------------------
Write-Host ""
Write-Host "[2/2] Installing Awesome-Grok-Skills (518 skills from LifeJiggy/Awesome-Grok-Skills)..." -ForegroundColor Yellow
Write-Host "      This may take a minute..." -ForegroundColor Gray

$tmpZip = "$env:TEMP\awesome-grok-skills.zip"
$tmpExtract = "$env:TEMP\awesome-grok-skills-extract"

try {
    Invoke-WebRequest -Uri "https://github.com/LifeJiggy/Awesome-Grok-Skills/archive/refs/heads/main.zip" `
        -OutFile $tmpZip -UseBasicParsing
    Write-Host "  Downloaded archive." -ForegroundColor Gray

    if (Test-Path $tmpExtract) { Remove-Item $tmpExtract -Recurse -Force }
    Expand-Archive -Path $tmpZip -DestinationPath $tmpExtract -Force
    Write-Host "  Extracted archive." -ForegroundColor Gray

    $sourceBase = "$tmpExtract\Awesome-Grok-Skills-main"
    $converted = 0

    # Skills (category/skill/GROK.md)
    $skillsRoot = Join-Path $sourceBase "skills"
    Get-ChildItem $skillsRoot -Directory | ForEach-Object {
        $category = $_.Name
        Get-ChildItem $_.FullName -Directory | ForEach-Object {
            $skillName = $_.Name
            $grokFile = Join-Path $_.FullName "GROK.md"
            if (Test-Path $grokFile) {
                $content = Get-Content $grokFile -Raw -Encoding UTF8
                $nameMatch = [regex]::Match($content, 'name:\s*"?([^"\r\n]+)"?')
                $descMatch = [regex]::Match($content, 'description:\s*"?([^"\r\n]+)"?')
                $skillDesc = if ($descMatch.Success) { $descMatch.Groups[1].Value.Trim() } else { "Use this skill for $skillName tasks." }
                $destFolderName = "grok-$category-$skillName"
                $destFolder = Join-Path $globalSkillsDir $destFolderName
                New-Item -ItemType Directory -Force -Path $destFolder | Out-Null
                $skillMd = "---`nname: $destFolderName`ndescription: >-`n  $skillDesc`n---`n`n"
                $bodyContent = [regex]::Replace($content, '^---[\s\S]*?---\s*', '', 'Multiline')
                Set-Content -Path (Join-Path $destFolder "SKILL.md") -Value ($skillMd + $bodyContent.TrimStart()) -Encoding UTF8
                $converted++
            }
        }
    }

    # Agents (agent-name/GROK.md)
    $agentsRoot = Join-Path $sourceBase "agents"
    Get-ChildItem $agentsRoot -Directory | ForEach-Object {
        $agentName = $_.Name
        $grokFile = Join-Path $_.FullName "GROK.md"
        if (Test-Path $grokFile) {
            $content = Get-Content $grokFile -Raw -Encoding UTF8
            $descMatch = [regex]::Match($content, 'description:\s*"?([^"\r\n]+)"?')
            $skillDesc = if ($descMatch.Success) { $descMatch.Groups[1].Value.Trim() } else { "Use this skill for $agentName agent tasks." }
            $destFolderName = "grok-agent-$agentName"
            $destFolder = Join-Path $globalSkillsDir $destFolderName
            New-Item -ItemType Directory -Force -Path $destFolder | Out-Null
            $skillMd = "---`nname: $destFolderName`ndescription: >-`n  $skillDesc`n---`n`n"
            $bodyContent = [regex]::Replace($content, '^---[\s\S]*?---\s*', '', 'Multiline')
            Set-Content -Path (Join-Path $destFolder "SKILL.md") -Value ($skillMd + $bodyContent.TrimStart()) -Encoding UTF8
            $converted++
        }
    }

    Write-Host "  [+] Installed $converted Grok skills." -ForegroundColor Green

    # Cleanup
    Remove-Item $tmpZip -Force -ErrorAction SilentlyContinue
    Remove-Item $tmpExtract -Recurse -Force -ErrorAction SilentlyContinue

} catch {
    Write-Host "  [!] Failed to install Awesome-Grok-Skills: $_" -ForegroundColor Red
}

# -------------------------------------------------------
# Done
# -------------------------------------------------------
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Done! Skills installed to:" -ForegroundColor Green
Write-Host "  $globalSkillsDir" -ForegroundColor Green
Write-Host "  Restart Antigravity IDE to load all skills." -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
