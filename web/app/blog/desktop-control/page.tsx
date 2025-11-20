import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Introducing Experimental Desktop Control - Weaszel Blog',
  description: 'Learn about Weaszel\'s new experimental desktop control feature, its capabilities, limitations, and when to use it.',
};

export default function DesktopControlBlogPost() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-black to-purple-900">
      <div className="container mx-auto px-6 py-20">
        <div className="max-w-4xl mx-auto">
          {/* Back to Blog */}
          <Link 
            href="/blog" 
            className="inline-flex items-center text-purple-300 hover:text-purple-200 mb-8 transition-colors"
          >
            ← Back to Blog
          </Link>

          {/* Article Header */}
          <article className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 md:p-12 border border-purple-500/30">
            <div className="mb-8">
              <span className="px-4 py-2 bg-yellow-500/20 text-yellow-300 rounded-full text-sm font-semibold">
                ⚠️ Experimental Feature
              </span>
              <h1 className="text-4xl md:text-5xl font-bold text-white mt-4 mb-4">
                Introducing Desktop Control: Power Meets Caution
              </h1>
              <div className="flex items-center gap-4 text-purple-300">
                <span>November 19, 2024</span>
                <span>•</span>
                <span>5 min read</span>
              </div>
            </div>

            {/* Introduction */}
            <div className="prose prose-invert prose-purple max-w-none">
              <p className="text-xl text-gray-300 leading-relaxed mb-6">
                With version 1.1.0, Weaszel gains the ability to control your local desktop applications—not just your browser. 
                This opens up powerful new automation possibilities, but it comes with important caveats you need to understand.
              </p>

              <div className="bg-yellow-500/10 border-l-4 border-yellow-500 p-6 my-8 rounded-r-lg">
                <p className="text-yellow-200 font-semibold mb-2">⚠️ Important Notice</p>
                <p className="text-yellow-100 text-sm">
                  Desktop Control is an <strong>experimental feature</strong>. It can be unreliable and requires elevated macOS permissions. 
                  We recommend sticking with Browser Automation (the default) unless you have a specific need for desktop control.
                </p>
              </div>

              <h2 className="text-3xl font-bold text-white mt-12 mb-4">What is Desktop Control?</h2>
              <p className="text-gray-300 mb-4">
                Desktop Control allows Weaszel to interact with any application on your Mac—TextEdit, Finder, VS Code, you name it. 
                Using macOS Accessibility APIs and AppleScript, the agent can:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 mb-6">
                <li>Open and close applications</li>
                <li>Click, type, and navigate within apps</li>
                <li>Execute AppleScript commands for advanced automation</li>
                <li>Take screenshots to understand the current state</li>
              </ul>

              <h2 className="text-3xl font-bold text-white mt-12 mb-4">✅ Pros: When Desktop Control Shines</h2>
              <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-6 mb-6">
                <ul className="space-y-3 text-gray-300">
                  <li className="flex items-start">
                    <span className="text-green-400 mr-3 text-xl">✓</span>
                    <div>
                      <strong className="text-green-300">Local App Automation:</strong> Automate tasks in native macOS apps like Notes, TextEdit, or Finder
                    </div>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-3 text-xl">✓</span>
                    <div>
                      <strong className="text-green-300">Beyond the Browser:</strong> Handle workflows that span both web and desktop (e.g., download a file, then open it in Preview)
                    </div>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-3 text-xl">✓</span>
                    <div>
                      <strong className="text-green-300">AppleScript Power:</strong> Execute complex macOS automation scripts for advanced users
                    </div>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-3 text-xl">✓</span>
                    <div>
                      <strong className="text-green-300">Unified Agent:</strong> One AI agent for all your automation needs, not just web tasks
                    </div>
                  </li>
                </ul>
              </div>

              <h2 className="text-3xl font-bold text-white mt-12 mb-4">❌ Cons: The Reality Check</h2>
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6 mb-6">
                <ul className="space-y-3 text-gray-300">
                  <li className="flex items-start">
                    <span className="text-red-400 mr-3 text-xl">✗</span>
                    <div>
                      <strong className="text-red-300">Flaky and Unreliable:</strong> Desktop automation is inherently fragile. Apps steal focus, coordinates shift, and timing issues are common.
                    </div>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-3 text-xl">✗</span>
                    <div>
                      <strong className="text-red-300">Requires Permissions:</strong> You must grant Screen Recording and Accessibility permissions to your terminal, which some users may find invasive.
                    </div>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-3 text-xl">✗</span>
                    <div>
                      <strong className="text-red-300">Slower Than Browser:</strong> Desktop actions involve more overhead and are generally slower than browser automation.
                    </div>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-3 text-xl">✗</span>
                    <div>
                      <strong className="text-red-300">macOS Only:</strong> This feature is currently exclusive to macOS due to reliance on AppleScript and Accessibility APIs.
                    </div>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-3 text-xl">✗</span>
                    <div>
                      <strong className="text-red-300">Can Get Stuck:</strong> If the agent misidentifies the active window or an app doesn't respond as expected, it may loop or fail.
                    </div>
                  </li>
                </ul>
              </div>

              <h2 className="text-3xl font-bold text-white mt-12 mb-4">🛡️ Safety & Permissions</h2>
              <p className="text-gray-300 mb-4">
                To use Desktop Control, you'll need to grant two macOS permissions to your terminal application (Terminal.app, iTerm, or VS Code):
              </p>
              <ol className="list-decimal list-inside text-gray-300 space-y-2 mb-6">
                <li><strong className="text-purple-300">Screen Recording:</strong> Allows Weaszel to see your screen and understand the current state</li>
                <li><strong className="text-purple-300">Accessibility:</strong> Allows Weaszel to control your mouse and keyboard</li>
              </ol>
              <p className="text-gray-300 mb-6">
                These are powerful permissions. Weaszel uses them responsibly, but you should be aware of what you're granting. 
                The agent will guide you through the setup process on first run.
              </p>

              <h2 className="text-3xl font-bold text-white mt-12 mb-4">🎯 Our Recommendation</h2>
              <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-6 mb-6">
                <p className="text-purple-200 mb-4">
                  <strong>Stick with Browser Automation unless you have a specific need for desktop control.</strong>
                </p>
                <p className="text-gray-300 mb-4">
                  Browser automation is:
                </p>
                <ul className="list-disc list-inside text-gray-300 space-y-2">
                  <li>More reliable and battle-tested</li>
                  <li>Faster and more efficient</li>
                  <li>Doesn't require invasive permissions</li>
                  <li>Covers 95% of automation use cases (job applications, research, shopping, etc.)</li>
                </ul>
              </div>

              <p className="text-gray-300 mb-6">
                Desktop Control is there for the 5% of cases where you truly need to interact with local apps. 
                Think of it as a power tool: incredibly useful in the right hands, but not something you reach for every day.
              </p>

              <h2 className="text-3xl font-bold text-white mt-12 mb-4">🚀 Getting Started</h2>
              <p className="text-gray-300 mb-4">
                When you run Weaszel for the first time (or after updating to v1.1.0), you'll see a clear choice:
              </p>
              <div className="bg-black/30 rounded-lg p-6 mb-6 font-mono text-sm">
                <p className="text-green-400 mb-2">1. Browser Automation (Recommended)</p>
                <p className="text-gray-400 mb-4">   - Stable, fast, and safe</p>
                <p className="text-yellow-400 mb-2">2. Full Desktop Control (Experimental)</p>
                <p className="text-gray-400">   - Can control your mouse and keyboard</p>
              </div>
              <p className="text-gray-300 mb-6">
                Simply press <code className="bg-black/30 px-2 py-1 rounded text-purple-300">1</code> (or just hit Enter) to stick with the recommended browser mode. 
                If you're feeling adventurous, press <code className="bg-black/30 px-2 py-1 rounded text-purple-300">2</code> and follow the permission setup guide.
              </p>

              <h2 className="text-3xl font-bold text-white mt-12 mb-4">🔮 The Future</h2>
              <p className="text-gray-300 mb-6">
                Desktop Control is experimental, and we're actively working to improve its reliability. Future updates may include:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 mb-6">
                <li>Better error recovery and retry logic</li>
                <li>Smarter window focus management</li>
                <li>Support for Windows and Linux (if there's demand)</li>
                <li>Pre-built automation scripts for common desktop tasks</li>
              </ul>

              <p className="text-gray-300 mb-6">
                Your feedback is crucial! If you try Desktop Control, let us know what works, what doesn't, and what you'd like to see improved.
              </p>

              <div className="bg-purple-500/10 border-l-4 border-purple-500 p-6 my-8 rounded-r-lg">
                <p className="text-purple-200 font-semibold mb-2">💡 Final Thoughts</p>
                <p className="text-purple-100">
                  Desktop Control is a glimpse into the future of AI agents—assistants that can truly work across your entire computer, not just the web. 
                  But it's early days. Use it wisely, report bugs, and help us make it better. 🦊
                </p>
              </div>

              <div className="mt-12 pt-8 border-t border-purple-500/30">
                <p className="text-gray-400 text-sm">
                  Questions or feedback? Reach out on <a href="https://github.com/smammadov1994/Weaszel" className="text-purple-400 hover:text-purple-300 underline">GitHub</a>.
                </p>
              </div>
            </div>
          </article>
        </div>
      </div>
    </div>
  );
}
