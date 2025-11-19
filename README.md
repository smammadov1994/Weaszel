# 🌰 Weaszel

> **Your Cozy AI Companion for the Web.**
>
> Weaszel lives in your terminal and surfs the web for you. From research to shopping, it handles the boring stuff so you can relax.

![Weaszel Screenshot](assets/screenshot.png)

## 🚀 Features

- **🦊 Stealth Mode:** Connects to your existing Chrome browser to bypass Cloudflare, Captchas, and bot detection effortlessly.
- **🧠 Gemini Powered:** Uses Google's latest `gemini-2.5-computer-use-preview` model to "see" and interact with the web.
- **⚡ Rapid Fire:** Automates repetitive tasks like job applications, form filling, and data entry.
- **🛡️ Full Control:** You own the agent. No hidden limits, no "safety" blocks on booking flights. It runs locally on your machine.

## 🛠️ Architecture

Weaszel uses a "Human-in-the-Loop" architecture powered by Google Gemini and Playwright.

![Architecture Diagram](assets/architecture.png)

1.  **Capture:** The agent takes a screenshot of your browser.
2.  **Analyze:** Gemini analyzes the screen and decides the next action (click, type, scroll).
3.  **Execute:** Playwright executes the action in your browser.
4.  **Repeat:** The loop continues until the task is done.

## 📦 Installation

You can install Weaszel with a single command:

```bash
curl -sL https://weaszel.com/install.sh | bash
```

Or manually:

1.  Clone the repo:
    ```bash
    git clone https://github.com/smammadov1994/Weaszel.git
    cd Weaszel/job-weasel-agent
    ```

2.  Install dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    playwright install chromium
    ```

3.  Run it:
    ```bash
    python weasel.py
    ```

## 🔑 Setup

1.  **Get a Gemini API Key:** [Google AI Studio](https://aistudio.google.com/app/apikey)
2.  **Launch Chrome (Optional):** For Stealth Mode, launch your Chrome with remote debugging:
    ```bash
    ./start_chrome.sh
    ```
3.  **Start Weaszel:** Follow the on-screen instructions to connect.

## 🤝 Contributing

Weaszel is open source! Feel free to open issues or submit PRs.

## ☕ Support

If Weaszel helps you save time (or land a job!), consider buying me a coffee.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/smammadov94)

---

*Built with ❤️ by Seymur.*
