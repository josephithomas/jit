"""
FastAPI Server for Universal SkillForge Studio.
Provides web UI and REST endpoints for document upload, text parsing, synthesis,
validation, and cross-platform installation.
"""

from __future__ import annotations
import os
import io
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from parser import DocumentParser
from synthesizer import SkillSynthesizer
from validator import SkillValidator
from installer import SkillInstaller

app = FastAPI(
    title="Titus SkillForge",
    description="Convert documents, prompts, and images into valid SKILL.md files for Claude, Grok, ChatGPT, Gemini, and Antigravity.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)


class SynthesizeRequest(BaseModel):
    raw_text: str
    skill_name: Optional[str] = None
    description: Optional[str] = None
    target_platforms: Optional[List[str]] = None
    author: Optional[str] = "Titus SkillForge Universal"
    version: Optional[str] = "1.0.0"
    boundary_level: Optional[str] = "standard"
    category: Optional[str] = "general"
    custom_tags: Optional[List[str]] = None
    gemini_api_key: Optional[str] = None


class ValidateRequest(BaseModel):
    markdown: str


class InstallRequest(BaseModel):
    skill_name: str
    markdown: str
    target: str
    workspace_path: Optional[str] = None


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        parsed = DocumentParser.parse_file(content, file.filename or "uploaded-file")
        return {
            "success": True,
            "filename": file.filename,
            "format": parsed.get("format"),
            "text": parsed.get("text", ""),
            "metadata": parsed.get("metadata", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@app.post("/api/synthesize")
async def synthesize_skill(req: SynthesizeRequest):
    if not req.raw_text or not req.raw_text.strip():
        raise HTTPException(status_code=400, detail="raw_text cannot be empty.")

    synth_res = SkillSynthesizer.synthesize(
        raw_text=req.raw_text,
        skill_name=req.skill_name,
        description=req.description,
        target_platforms=req.target_platforms,
        author=req.author or "Titus SkillForge Universal",
        version=req.version or "1.0.0",
        boundary_level=req.boundary_level or "standard",
        category=req.category or "general",
        custom_tags=req.custom_tags,
        gemini_api_key=req.gemini_api_key
    )

    val_res = SkillValidator.validate_content(synth_res["markdown"])

    return {
        "success": True,
        "name": synth_res["name"],
        "markdown": synth_res["markdown"],
        "frontmatter": synth_res["frontmatter"],
        "validation": val_res
    }


@app.post("/api/validate")
async def validate_skill(req: ValidateRequest):
    val_res = SkillValidator.validate_content(req.markdown)
    return {
        "success": True,
        "validation": val_res
    }


@app.post("/api/export/zip")
async def export_zip(req: SynthesizeRequest):
    name = SkillSynthesizer.slugify(req.skill_name or "universal-skill")
    synth_res = SkillSynthesizer.synthesize(
        raw_text=req.raw_text,
        skill_name=name,
        description=req.description,
        target_platforms=req.target_platforms,
        boundary_level=req.boundary_level or "standard",
        gemini_api_key=req.gemini_api_key
    )
    zip_bytes = SkillInstaller.create_zip_package(synth_res["name"], synth_res["markdown"])

    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={synth_res['name']}-skill-package.zip"}
    )


@app.post("/api/install")
async def install_skill(req: InstallRequest):
    clean_name = SkillSynthesizer.slugify(req.skill_name)
    if req.target == "antigravity":
        result = SkillInstaller.install_to_antigravity(clean_name, req.markdown)
    elif req.target == "claude":
        result = SkillInstaller.install_to_claude(clean_name, req.markdown)
    elif req.target == "workspace":
        ws = req.workspace_path or os.getcwd()
        result = SkillInstaller.install_to_workspace(clean_name, req.markdown, ws)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown install target: {req.target}")

    return result


@app.get("/api/templates")
async def get_templates():
    templates = [
        {
            "id": "security-audit",
            "name": "Security & Vulnerability Audit",
            "category": "security",
            "boundary": "read-only",
            "sample_text": """Standard Operating Procedure: Automated Security & Vulnerability Audit
Purpose: Run systematic security reviews of source code, dependencies, and configuration.
Scope: Scan for hardcoded credentials, API keys, outdated CVEs, insecure cryptographic algorithms, and OWASP Top 10 flaws.
Workflow:
1. Scan git history and working tree for secrets, API tokens, and private keys.
2. Review dependency manifests (package.json, requirements.txt, go.mod) against known vulnerability databases.
3. Inspect route definitions and controller endpoints for authorization bypass and parameter injection.
4. Verify HTTP security headers (CSP, HSTS, X-Content-Type-Options) and CORS configurations.
5. Generate structured triage report with severity ratings (Critical, High, Medium, Low) and concrete remediation diffs.
Rules:
- Strictly read-only: never execute destructive exploit payloads or disclose live secrets in logs.
- Never output raw passwords or production credentials into public artifacts.
- Produce actionable fix snippets for every flagged issue."""
        },
        {
            "id": "code-review",
            "name": "Elite Code Reviewer",
            "category": "development",
            "boundary": "standard",
            "sample_text": """Standard Operating Procedure: Pull Request & Code Quality Review
Purpose: Provide thorough, constructive, and actionable code reviews for pull requests.
Checklist:
1. Review architectural patterns and design consistency with existing codebase.
2. Verify test coverage, edge cases, error recovery, and null/undefined handling.
3. Check performance bottlenecks (unindexed queries, unnecessary re-renders, N+1 lookups).
4. Inspect type safety, immutability, and naming clarity.
5. Offer concrete drop-in code diffs for all suggested improvements.
Boundaries:
- Respect author style when logically sound; do not stall on subjective aesthetic bike-shedding.
- Always provide reasoning for suggested changes."""
        },
        {
            "id": "devops-pipeline",
            "name": "DevOps & CI/CD Deployment Orchestrator",
            "category": "devops",
            "boundary": "high-consequence",
            "sample_text": """Procedure: Production Deployment and Release Verification
Purpose: Orchestrate safe CI/CD build, container deployment, health checks, and rollbacks.
Workflow:
1. Pre-flight verification: Run unit tests, lint checks, and security scans on release candidate.
2. Build container image, compute sha256 digest, and push to container registry.
3. Apply declarative infrastructure manifests with canary or blue-green traffic split.
4. Monitor live telemetry (error rates, p99 latency, CPU utilization) for 5 minutes.
5. If anomalies exceed 1% threshold, automatically execute zero-downtime rollback.
Boundaries:
- High consequence: Production deployments require explicit authorization before executing migration scripts.
- Never bypass broken pre-flight checks."""
        }
    ]
    return {"templates": templates}


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Titus SkillForge Running.</h1>")
