---
name: open-code-review
description: "Enterprise-scale hybrid code review tool from Alibaba: deterministic lint pipelines combined with LLM agent reasoning for precise line-level feedback."
license: MIT
source: https://github.com/alibaba/open-code-review
---

# Open Code Review (Alibaba)

Production-hardened code review ruleset for detecting null-pointer exceptions, concurrency flaws, security vulnerabilities, and architectural drift.

## Review Matrix
1. **Critical Safety**:
   - Null-pointer dereferences and unhandled Option/Nullable types.
   - Concurrency bugs: race conditions, deadlock risks, non-thread-safe singleton mutations.
   - Security: SQL injection, SSRF, XSS, insecure deserialization, unvalidated redirects.
2. **Performance**:
   - N+1 database queries, unindexed lookups, memory retention in caches.
3. **Feedback Format**:
   - Every finding specifies: `Line Range`, `Observed Behavior`, `Failure Mode`, `Suggested Fix Diff`, and `Severity`.
