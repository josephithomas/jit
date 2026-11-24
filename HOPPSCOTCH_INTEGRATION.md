# Hoppscotch Integration Guide (ECC-style) for `jit`

Adds **[Hoppscotch](https://github.com/hoppscotch/hoppscotch)** (open-source API testing) to this repo, and wires it into your Claude Code agents and skills (ECC) so an agent can test your APIs for you.

Everything below is for **Windows PowerShell**. Copy one block at a time.

> Sources: Hoppscotch CLI docs (docs.hoppscotch.io/documentation/clients/cli) and the ECC README. If a flag ever behaves differently, run `hopp test --help` — the CLI is the final authority.

---

## What you get

| Piece | What it does |
|---|---|
| `hopp` (Hoppscotch CLI) | Runs a Hoppscotch collection from the terminal and checks each request's test script. |
| `hoppscotch/` folder | Holds your exported collections and environment files. |
| `skills/hoppscotch-api-testing/SKILL.md` | Teaches your AI agent when and how to use `hopp`. |
| `.github/workflows/api-tests.yml` | Runs the same tests automatically on every push. |

---

## Step 0 - What you need first

1. **Node.js 22** - use v22 exactly. Node 25 failed to build the CLI on Windows (it needs a C++ compiler for a package called `isolated-vm`). Download the `-x64.msi` from https://nodejs.org/dist/latest-v22.x/ (winget may not work on your PC).
2. **Git**.

Check both:

```powershell
node --version
git --version
```

`node --version` must print `v22.something`. If it prints another version, uninstall Node (run `appwiz.cpl`, click Node.js, then Uninstall), install the Node 22 `.msi`, then **close and reopen PowerShell**.

---

## Step 1 - Install the Hoppscotch CLI

```powershell
npm install -g @hoppscotch/cli
hopp -v
```

The version flag is `-v` (not `--version`). If PowerShell says `hopp` is not recognized, close PowerShell, open a new one, and try again.

---

## Step 2 - Get the repo and make the folders

```powershell
git clone https://github.com/josephithomas/jit.git
cd jit
New-Item -ItemType Directory -Force hoppscotch\collections, hoppscotch\environments | Out-Null
```

---

## Step 3 - Export your collection from Hoppscotch

1. Open Hoppscotch (https://hoppscotch.io or the desktop app).
2. Build requests in a **Collection**. In each request's **Tests** tab, add checks (for example, status code is 200).
3. Click the collection's **...** menu, then **Export**, and save it as:
   `hoppscotch\collections\my-api.json`
4. Open **Environments**, export your environment (one environment at a time) and save it as:
   `hoppscotch\environments\local.env.json`

> Tip: use `<<baseurl>>` in your request URLs and set `baseurl` in the environment file. You can then switch between local and live without editing requests.
> The CLI only accepts a single-environment export (or the legacy format), **not** a bulk environment export.

The environment file the CLI accepts looks exactly like this (no `v` field):

```json
{
  "name": "ecc",
  "variables": [
    { "key": "GITHUB_API", "value": "https://api.github.com" }
  ]
}
```

**Always export collections from the Hoppscotch app.** A hand-written collection that is not in Hoppscotch's own format fails with `MALFORMED_COLLECTION`. A minimal working collection (verified to pass with CLI 0.31.4) is a collection at `v: 2` containing a request at `v: "3"` with `name`, `method`, `endpoint`, `params`, `headers`, `preRequestScript`, `testScript`, `auth`, `body` and `requestVariables`.

---

## Step 4 - Run your first test

```powershell
hopp test .\hoppscotch\collections\my-api.json -e .\hoppscotch\environments\local.env.json
```

Useful extras:

```powershell
# Wait 500 ms between requests
hopp test .\hoppscotch\collections\my-api.json -e .\hoppscotch\environments\local.env.json -d 500

# Save a JUnit XML report (CI tools can read it)
hopp test .\hoppscotch\collections\my-api.json -e .\hoppscotch\environments\local.env.json --reporter-junit .\hoppscotch\report.xml
```

Note: a non-200 response (like 404) is still a valid response. Pass or fail is decided by your test scripts.

---

## Step 5 - Keep secrets out of GitHub

Never commit API keys or tokens.

```powershell
Add-Content .gitignore "`nhoppscotch/report.xml`nhoppscotch/environments/*.secret.json"
```

Per the Hoppscotch docs, for secret variables either:
- put the secret in your PowerShell session (`$env:MY_SECRET = "value"`), or
- put it in a local env file named `*.secret.json` (ignored by git above).

---

## Step 6 - (Optional) Run a collection stored in Hoppscotch cloud or self-hosted

```powershell
$env:HOPP_TOKEN = "paste-your-personal-access-token"
hopp test <collection-id> --token $env:HOPP_TOKEN
# Self-hosted server:
hopp test <collection-id> --token $env:HOPP_TOKEN --server https://hoppscotch.your-company.com
```

Find the collection ID in Hoppscotch: collection **...** menu, **Run Collection**, **CLI** tab (it pre-fills the command for you).

---

## Step 7 - Give the skill to your AI agent (the ECC part)

Create the skill file inside this repo (the `jit` repo already has a `skills/` folder):

```powershell
New-Item -ItemType Directory -Force skills\hoppscotch-api-testing | Out-Null
@'
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
2. Run: `hopp test <collection.json> -e <environment.json>`
3. For CI output add: `--reporter-junit hoppscotch/report.xml`
4. Never print or commit secrets. Read them from environment variables.
5. A non-200 status is still a valid response; failures come from test scripts. Check the test script before blaming the API.

## If it fails
- `hopp` not found: run `npm install -g @hoppscotch/cli` (Node 22+).
- Variables not substituted: the env file is probably a bulk export. Re-export a single environment.
'@ | Set-Content -Encoding UTF8 skills\hoppscotch-api-testing\SKILL.md
```

Install it for Claude Code (copies the skill to your personal skills folder):

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force skills\hoppscotch-api-testing "$HOME\.claude\skills\"
```

Restart Claude Code. Now ask it: *"Use the hoppscotch-api-testing skill to test my API."*

If you also use your ECC fork (`josephithomas/ecc`), you can copy the same folder into its `skills\` directory so it ships with the rest of your ECC skills:

```powershell
Copy-Item -Recurse -Force skills\hoppscotch-api-testing <path-to-your-ecc-clone>\skills\
```

---

## Step 8 - Run the tests automatically on GitHub

```powershell
New-Item -ItemType Directory -Force .github\workflows | Out-Null
@'
name: API tests
on: [push, pull_request]
jobs:
  hopp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm i -g @hoppscotch/cli
      - run: hopp test ./hoppscotch/collections/my-api.json -e ./hoppscotch/environments/ci.env.json --reporter-junit ./report.xml
'@ | Set-Content -Encoding UTF8 .github\workflows\api-tests.yml
```

Create `hoppscotch\environments\ci.env.json` (an environment export that points at a URL GitHub can reach, with no secrets inside). Put real secrets in GitHub: repo **Settings, Secrets and variables, Actions**.

---

## Step 9 - Commit and push to GitHub

```powershell
git checkout -b add-hoppscotch
git add HOPPSCOTCH_INTEGRATION.md hoppscotch skills\hoppscotch-api-testing .github\workflows\api-tests.yml .gitignore
git status
git commit -m "docs: add Hoppscotch API testing integration guide, skill and CI workflow"
git push -u origin add-hoppscotch
```

Open the link GitHub prints, create the pull request, and merge it. (To skip the PR, use `git checkout main` then `git merge add-hoppscotch` then `git push`.)

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `hopp` is not recognized | Reopen PowerShell. Still failing: `npm config get prefix` and make sure that folder is on your PATH. |
| `MALFORMED_ENV_FILE` | Use the exact env format shown in Step 3 (`name` + `variables` with `key`/`value`). |
| `MALFORMED_COLLECTION` | The file was hand-written. Export the collection from the Hoppscotch app instead. |
| `npm install -g @hoppscotch/cli` fails with `gyp ERR! find VS` | You are on a Node version that is too new (25). Install Node 22. |
| `unknown option '--version'` | Use `hopp -v`. |
| Variables like `<<baseurl>>` not replaced | Re-export a **single** environment (not bulk) and pass it with `-e`. |
| Script says "running scripts is disabled" | Run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Test passes locally but fails in CI | CI cannot reach `localhost`. Use a public or test URL in `ci.env.json`. |
| Unsure about a flag | `hopp test --help` |
