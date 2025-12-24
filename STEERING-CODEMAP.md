# Code Map (Weaszel)

### Top-level

- `job-weasel-agent/`: Python CLI agent runtime (the core product)
- `web/`: Next.js site (marketing/blog/installer hosting)
- `assets/`: images/screenshots used by README/site
- `pyproject.toml`: Python deps (Browser-Use, Playwright, Gemini bindings, etc.)

### Python agent (`job-weasel-agent/`)

- `weasel.py`
  - CLI entrypoint, env loading, interactive loop, validator/router, calls planner + agent.
- `browser_agent.py`
  - Browser-Use wrapper; runs web tasks; prints cost estimate; hooks retries.
- `query_planner.py`
  - Task analysis + clarifying questions + “enhanced task” generation.
- `retry_controller.py`
  - Failure tracking and escalating recovery strategies (replan/switch site/ask user).

Legacy/desktop:

- `legacy_agent.py`
  - Gemini Computer Use loop + tool call handling (legacy approach).
- `desktop_computer.py`
  - “Computer” implementation for desktop mode (currently minimal/stub).
- `desktop_functions.py`
  - Custom desktop functions available to the legacy agent (AppleScript-based).
- `computers/`
  - `computer.py`: `Computer` ABC + `EnvState` model for the legacy agent.

User data:

- `user_data.md`
  - User profile instructions/data appended to tasks (should be treated as user-local).

### Website (`web/`)

- `web/app/`
  - Next.js App Router pages (home, blog posts, changelog).
- `web/public/install.sh`
  - Installer that clones into `~/.weaszel`, runs `uv sync`, installs Chromium, and adds a `weaszel` alias.


