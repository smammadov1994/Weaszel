#!/bin/bash
echo "🚀 Launching Google Chrome with Remote Debugging..."
echo "⚠️  Please close all other Chrome windows first!"

"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 --no-first-run --no-default-browser-check --user-data-dir="/tmp/chrome-debug-profile" &

echo "✅ Chrome launched on port 9222"
echo "You can now run 'python weasel.py' to connect to it."
