# Weaszel - AI Agent for Web Automation

**Powered by Google Gemini & Browser-Use**

## Quick Start

### 1. Installation

**Clone the Repository**

```bash
git clone https://github.com/your-org/weaszel.git
cd weaszel
```

**Set up with UV (Recommended)**

```bash
# Install dependencies with uv
uv sync

# Install Playwright browsers
uvx playwright install chromium
```

### 2. Configuration

Create a `.env.local` file in the project root:

```bash
GEMINI_API_KEY=your_api_key_here
EXPERIMENTAL_DESKTOP_ENABLED=false
```

Get your Gemini API key from: https://aistudio.google.com/app/apikey

### 3. Running Weaszel

```bash
uv run python job-weasel-agent/weasel.py
```

You'll be greeted with an interactive prompt. Try asking:
- "Go to Amazon and find a mechanical keyboard"
- "Find the latest AI news on TechCrunch"
- "Search for cheap flights to Tokyo"

## Architecture

Weaszel uses a **hybrid architecture**:

- **Browser Tasks** (Default): Powered by [Browser-Use](https://github.com/browser-use/browser-use) framework with Gemini 2.0 Flash
  - Fast, reliable web automation
  - Intelligent navigation and data extraction
  - Built-in error handling and retries

- **Desktop Tasks** (Legacy): Falls back to Gemini Computer Use for local app control
  - Available when `EXPERIMENTAL_DESKTOP_ENABLED=true`
  - Can control local apps like Calculator, TextEdit, etc.
  - Requires macOS Accessibility permissions

## Key Files

- `job-weasel-agent/weasel.py` - Main entry point
- `job-weasel-agent/browser_agent.py` - Browser-Use wrapper
- `job-weasel-agent/legacy_agent.py` - Desktop computer agent
- `job-weasel-agent/user_data.md` - Store personal info for agents to use

## Features

✅ Natural language web automation  
✅ Smart task routing (browser vs desktop)  
✅ User profile support (`user_data.md`)  
✅ Safety confirmations for risky actions  
✅ Rich terminal UI with progress tracking  

## Troubleshooting

**Browser doesn't launch:**
```bash
uvx playwright install chromium
```

**API key issues:**
- Ensure your key starts with `AIza...`
- Check it's set in `.env.local` in the project root

**Desktop control not working:**
- Set `EXPERIMENTAL_DESKTOP_ENABLED=true` in `.env.local`
- Grant Accessibility permissions to your terminal app

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

Apache 2.0 - See [LICENSE](LICENSE)
