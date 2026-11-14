---
name: vibe-security-skill
description: >-
  Agent skill that audits vibe-coded (and any) apps for common security
  vulnerabilities introduced by AI coding assistants: secrets, RLS, auth,
  payments, rate limits, mobile, AI/LLM, deployment, and data-access flaws.
license: MIT
source: https://github.com/raroque/vibe-security-skill
compatibility: Claude Code, OpenAI Codex, Agent Skills format hosts
metadata:
  grok:
    tags: [vibe security, security audit, secrets, RLS, auth, payments, AI security]
    related_skills: [awesome-vibe-coding-resources, free-claude-code, impeccable]
---

# Vibe Security Skill

Security audit skill for vibe-coded apps (and general apps). Catches patterns AI assistants commonly introduce: hardcoded secrets, weak RLS, client-trusted prices, tokens in localStorage, missing rate limits, etc.

**Standing instruction for this workspace:** Use this skill while vibe coding — run security checks on auth, payments, DB access, API keys, and user data before shipping.

## When to Activate

- Any vibe-coding session (default / standing)
- Writing or reviewing auth, payments, database access, API keys, or user data
- Explicit: "check security", "audit this", "is this safe?", `/vibe-security`

## Core Powers

| Category | Catches |
|----------|---------|
| Secrets & env | Hardcoded keys, public env leaks, missing .gitignore |
| Database | Disabled/weak Supabase RLS, Firebase open rules, missing auth |
| Auth | Unverified JWT, middleware-only auth, tokens in localStorage |
| Rate limiting | Missing limits on auth/AI/email, client-tamperable counters |
| Payments | Client-submitted prices, missing webhook verification |
| Mobile | Keys in JS bundle, AsyncStorage tokens, weak biometrics |
| AI / LLM | Exposed AI keys, no usage caps, prompt injection |
| Deployment | Debug in prod, source maps, missing headers |
| Data access | SQL injection, Prisma operator injection, mass assignment |

Technology-scoped reference files load only relevant checks (e.g. Supabase → RLS).

## Quick Activation

```bash
npx skills add https://github.com/raroque/vibe-security-skill --skill vibe-security
```

Or clone and point the agent at the skill folder on demand (do not bulk-vendor into jit).

## Operating Rules for This Workspace

1. **Standing:** Apply during vibe coding sessions; audit before ship when auth/payments/DB/secrets are involved.
2. Keep this thin entry only — no bulk copy of upstream skill tree into jit.
3. Follow full Standing Instructions in `RULES.md` on every use.

## Source

https://github.com/raroque/vibe-security-skill
