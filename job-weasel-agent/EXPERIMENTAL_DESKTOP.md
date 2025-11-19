# Experimental Desktop Control Branch

⚠️ **WARNING**: This is an experimental feature that gives the AI ability to control your desktop. Use with caution!

## What's New

This branch adds **desktop automation** capabilities to Weaszel. The AI can now:

### Desktop Functions

1. **`open_app(app_name)`** - Opens macOS applications
   - Example: "Open Finder", "Open Calculator", "Open Notes"

2. **`execute_applescript(script)`** - Runs AppleScript commands
   - Example: Advanced macOS automation

## How It Works

The agent now has **both** browser and desktop tools available:

1. **User gives a query**: "Open Finder" or "Search for keyboards on Amazon"
2. **Model decides which tools to use**:
   - Browser tasks → Uses browser tools (`click_at`, `navigate`, etc.)
   - Desktop tasks → Uses desktop tools (`open_app`, `execute_applescript`)
3. **Agent executes the appropriate actions**

## Example Commands

### Desktop Control
```bash
$ weaszel
> Open the Finder app
🖥️  Desktop action: open_app
✅ Result: {'status': 'success', 'app_name': 'Finder', 'message': 'Opened Finder'}
```

### Browser Control (still works!)
```bash
> Find me the best mechanical keyboard under $100 on Amazon
🌐 Navigating to Amazon...
```

### Mixed Usage
```bash
> Open Calculator and also search for the weather in Tokyo on Google
🖥️  Opens Calculator
🌐 Navigates to Google and searches
```

## Safety Warnings

⚠️ **This is experimental and potentially dangerous:**

- The AI can execute **any command** on your Mac via AppleScript
- It can open apps, move files, and interact with your system
- **Always supervise** what it's doing
- Use in a **test environment** or **virtual machine** if possible

## Testing Instructions

1. **Checkout this branch**:
   ```bash
   cd ~/.weaszel/job-weasel-agent
   git fetch
   git checkout experimental-desktop
   ```

2. **Run Weaszel**:
   ```bash
   weaszel
   ```

3. **Try a desktop command**:
   ```
   > Open Finder
   ```

## Switching Back to Safe Mode

To go back to browser-only (safe) mode:

```bash
cd ~/.weaszel/job-weasel-agent
git checkout main
```

## Future Improvements

Potential additions:
- [ ] File system operations (create, move, delete files)
- [ ] Screenshot capture
- [ ] System notifications
- [ ] More specific app controls (e.g., "Create a new note in Notes app")
- [ ] Cross-platform support (Windows, Linux)

## Technical Details

### New Files
- `desktop_functions.py` - Desktop automation function implementations

### Modified Files  
- `agent.py` - Added desktop function handling and execution

### Function Declarations
Desktop functions are registered as **custom user-defined functions** (as shown in Gemini Computer Use docs), allowing the model to call them alongside browser tools.

---

**Remember**: This is experimental. Report issues on the GitHub repo if you encounter bugs!
