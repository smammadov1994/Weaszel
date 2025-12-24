# Setup & Runbook (Weaszel)

### What you’re running

- **CLI agent**: `job-weasel-agent/weasel.py`
- **Website**: `web/` (optional; separate Next.js app)

### Requirements

- **Python**: 3.12+ (project requires `>=3.12`)
- **Playwright Chromium**: required for Browser-Use (web automation)
- **Gemini API key**: `GEMINI_API_KEY`

### Install (CLI agent)

From repo root:

```bash
uv sync
uv run playwright install chromium
```

### Configure

Create `.env.local` in the repo root:

```bash
GEMINI_API_KEY=your_key_here
EXPERIMENTAL_DESKTOP_ENABLED=false
```

Notes:
- The CLI loads `.env.local` from the **current working directory** (repo root).
- `EXPERIMENTAL_DESKTOP_ENABLED=true` enables the legacy “desktop control” path. It is currently experimental and limited (see `STEERING-RESISTANCE.md`).

### Run (CLI)

```bash
uv run python job-weasel-agent/weasel.py
```

### Install via script (optional)

The site’s installer script (`web/public/install.sh`) installs into `~/.weaszel` and adds a shell alias `weaszel` that runs the CLI.

### Run (website)

```bash
cd web
npm install
npm run dev
```

### Troubleshooting

- **Chromium missing / browser fails to launch**:

```bash
uv run playwright install chromium
```

- **“GEMINI_API_KEY not found”**:
  - Ensure `.env.local` exists at repo root and contains `GEMINI_API_KEY=...`.
  - Or export it for the session: `export GEMINI_API_KEY=...`

- **Captcha / safety blocks**:
  - Browser automation will often require manual captcha solves. Expect occasional “human in the loop”.


