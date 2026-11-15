---
name: build-your-own-x
description: >-
  Master programming by recreating favorite technologies from scratch.
  Curated compilation of high-quality, step-by-step guides for building
  databases, shells, Git, Redis, Docker, operating systems, neural nets,
  web servers, 3D renderers, blockchains, and dozens more systems from first principles.
license: CC0-1.0 (list itself); individual tutorials retain their own licenses
source: https://github.com/codecrafters-io/build-your-own-x
compatibility: Reference catalog + learning resource for any coding agent or developer
metadata:
  grok:
    tags: [build from scratch, systems programming, tutorials, learning, first principles, codecrafters]
    related_skills: [karpathy-guidelines, agent-rules-books, essential-claude-skills, free-claude-code]
---

# Build Your Own X

**Source**: https://github.com/codecrafters-io/build-your-own-x  
**Maintainer**: CodeCrafters, Inc. (originally started by Daniel Stefanovic)  
**Stars**: ~560k+

> What I cannot create, I do not understand — Richard Feynman.

A massive, high-signal curated list of well-written, step-by-step guides for re-creating core technologies from scratch. Ideal for deep learning, systems understanding, interview preparation, and reverse-engineering practice.

## When to Activate

- User wants to understand how a technology works by building it
- Need high-quality "from scratch" tutorials (Redis, Git, SQLite, Docker, shell, HTTP server, DNS, BitTorrent, neural nets, OS, databases, etc.)
- Looking for learning paths that emphasize first principles over frameworks
- Researching implementation details or alternative approaches for systems components
- Vibe-coding / reverse-engineering sessions that require ground-up understanding

## Core Powers / Categories Covered

- 3D Renderer / Ray tracing / Soft engines
- AI Model / LLM / Diffusion / RAG from scratch
- BitTorrent Client
- Blockchain / Cryptocurrency
- Database (B+ trees, Redis, SQLite-style, vector DB)
- Docker / Containers
- Emulator / Virtual Machine
- Git
- Network Stack / HTTP Server / DNS Server
- Neural Network
- Operating System
- Programming Language / Interpreter / Compiler
- Regex Engine
- Shell
- Web Browser / Web Server
- And many more (physics engines, text editors, search engines, memory allocators, etc.)

## Quick Activation / Usage

Browse the live curated list:

```bash
# View or clone the catalog (shallow clone preferred for token economy)
git clone --depth 1 https://github.com/codecrafters-io/build-your-own-x.git
```

Or open directly: https://github.com/codecrafters-io/build-your-own-x

When a specific technology is requested (e.g. "build your own Redis" or "Git from scratch"), surface the matching high-quality tutorials from the list and prefer the most complete / recently maintained ones.

## Operating Rules (Must Abide by Standing Instructions)

This skill is governed by the permanent standing instructions in `RULES.md`. In particular:

1. **Results & Objectives Above All** — Deliver the needed understanding or working reconstruction. Prefer the shortest path to a correct, functional outcome.
2. **GitHub Space Anchor** — All work, clones, branches, and derived code live under or are referenced from `https://github.com/josephithomas/jit`. Never create parallel skill trees or massive copies outside `skills/`.
3. **Thin Entry Only** — Treat this as a reference catalog. Do **not** copy the full README, tutorial list, or any large upstream content into jit. Keep only this SKILL.md.
4. **Vibe-Coding & Reverse-Engineering Protocol** — When implementing, use public guides to understand and reconstruct features surgically. Translate requirements into working code, verify, and keep Git hygiene clean.
5. **Token Economy** — Prefer shallow clones, surgical reads, and high signal-to-token ratio. Cache useful facts about specific tutorials once discovered.
6. **Jurisprudential Canons** — Apply necessity, proportionality, and contextual interpretation. Prefer the simplest sufficient tutorial path; discard over-engineering.
7. **Karpathy Standards** — Simplicity first, surgical changes, goal-driven execution.

Follow the full `RULES.md` on every use.

## Source

https://github.com/codecrafters-io/build-your-own-x
