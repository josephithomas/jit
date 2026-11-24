---
name: hoppscotch-api-testing
description: Run and write API tests with the Hoppscotch CLI (hopp test). Use when the user asks to test an API, verify endpoints, check a collection, or add API checks to CI.
---

# Hoppscotch API Testing

## When to use
- The user wants to test or verify an HTTP/GraphQL API.
- A change touched an endpoint and needs a regression check.
- The user wants API tests in GitHub Actions.

## How
1. Collections live in `hoppscotch/collections/*.json`; environments in `hoppscotch/environments/*.json`.
2. Run: `hopp test <collection.json> --env <environment.json>`
3. For CI output add: `--reporter-junit hoppscotch/report.xml`
4. Never print or commit secrets. Read them from environment variables.
5. A non-200 status is still a valid response; failures come from test scripts.

## If it fails
- `hopp` not found: `npm install -g @hoppscotch/cli` (Node 22 exactly).
- `MALFORMED_COLLECTION`: export the collection from the Hoppscotch app.
- `MALFORMED_ENV_FILE`: env file must be {"name": "...", "variables": [{"key": "...", "value": "..."}]}.