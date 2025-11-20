# Weaszel 2.0 🦊

**Your Cozy AI Companion for Web Automation**

Weaszel is a powerful, local-first AI agent that automates web tasks using natural language. Built with [Browser-Use](https://github.com/browser-use/browser-use) and Google Gemini 2.0.

## ✨ What's New in 2.0

- ⚡ **3-5x faster** task completion with Browser-Use framework
- 🧹 **Removed 2000+ lines** of complex browser control code
- 🛡️ **Built-in retry logic** and error recovery
- 🧠 **Gemini 2.0 Flash** optimized for speed and reliability

## 🚀 Quick Start

```bash
curl -sL https://weaszel.com/install.sh | bash
```

Then restart your terminal and run:
```bash
weaszel
```

## 💡 What Can It Do?

- 🔍 **Research**: "Find the latest AI news on TechCrunch"
- 🛒 **Shopping**: "Find a mechanical keyboard on Amazon under $100"
- ✈️ **Travel**: "Search for flights to Tokyo on Kayak"
- 📝 **Job Applications**: "Apply to software engineer jobs in NYC"
- 🌐 **Any Web Task**: Just ask!

## 🏗️ Architecture

Weaszel 2.0 uses a hybrid architecture:
- **Browser Tasks** (Default): Powered by Browser-Use + Gemini 2.0 Flash
- **Desktop Tasks** (Opt-in): Legacy implementation for local app control

## 📋 Requirements

- Python 3.12+
- macOS, Linux, or Windows
- Gemini API Key ([get one here](https://aistudio.google.com/app/apikey))

## 🔧 Manual Installation

```bash
# Clone the repository
git clone https://github.com/smammadov1994/Weaszel.git
cd Weaszel

# Install dependencies
uv sync

# Install browser
uv run playwright install chromium

# Run Weaszel
uv run python job-weasel-agent/weasel.py
```

## 🌐 Learn More

- [Blog: Weaszel 2.0 Release](https://weaszel.com/blog/v2-release)
- [Documentation](https://weaszel.com)
- [GitHub](https://github.com/smammadov1994/Weaszel)

## ☕ Support

If Weaszel helps you save time, consider [buying me a coffee](https://buymeacoffee.com/surfingcoin)!

## 📜 License

Apache 2.0 - See [LICENSE](LICENSE)

---

*Built with 🌰 by Seymur*
