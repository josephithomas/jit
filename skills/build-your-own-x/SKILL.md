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
# View or clone the catalog
git clone --depth 1 https://github.com/codecrafters-io/build-your-own-x.git
```

Or open directly: https://github.com/codecrafters-io/build-your-own-x

When a specific technology is requested (e.g. "build your own Redis" or "Git from scratch"), surface the matching high-quality tutorials from the list and prefer the most complete / recently maintained ones.

## Operating Rules for This Workspace

1. Treat as a **reference catalog + learning resource**, not a bulk-install skill pack.
2. Do **not** copy the full README or tutorial list into jit — keep this thin entry only.
3. Prefer primary upstream tutorial links; verify they are still live and high quality before recommending.
4. When implementing, follow Karpathy-style simplicity, surgical changes, and the standing rules in `RULES.md`.
5. Excellent companion to reverse-engineering / vibe-coding sessions and to the free-claude-code harnesses.

## Source

https://github.com/codecrafters-io/build-your-own-x
