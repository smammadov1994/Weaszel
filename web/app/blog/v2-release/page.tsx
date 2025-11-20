import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Weaszel 2.0: 3-5x Faster with Browser-Use - Weaszel Blog',
  description: 'Weaszel 2.0 is here! We migrated to the Browser-Use framework for 3-5x faster task completion, simpler code, and improved reliability.',
};

export default function V2ReleaseBlogPost() {
  return (
    <div className="min-h-screen bg-[#1c1917] text-[#e7e5e4] font-mono">
      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 border-b border-stone-800 bg-[#1c1917]/90 backdrop-blur-md">
        <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link 
            href="/blog" 
            className="flex items-center gap-2 text-amber-600 hover:text-amber-500 transition-colors"
          >
            ← Back to Blog
          </Link>
        </div>
      </nav>

      {/* Content */}
      <div className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto">
          {/* Article Header */}
          <article className="bg-[#0c0a09] border border-amber-900/30 rounded-2xl p-8 md:p-12">
            <div className="mb-8">
              <span className="px-4 py-2 bg-green-900/20 text-green-400 rounded-full text-sm font-bold border border-green-800/30">
                🚀 Major Release
              </span>
              <h1 className="text-4xl md:text-5xl font-bold text-stone-100 mt-4 mb-4">
                Weaszel 2.0: Faster, Simpler, Better
              </h1>
              <div className="flex items-center gap-4 text-stone-500">
                <span>November 20, 2024</span>
                <span>•</span>
                <span>8 min read</span>
              </div>
            </div>

            {/* Introduction */}
            <div className="prose prose-invert prose-stone max-w-none">
              <p className="text-xl text-stone-400 leading-relaxed mb-6">
                Today, we're thrilled to announce Weaszel 2.0—a complete reimagining of how Weaszel automates your browser. 
                By migrating to the open-source <a href="https://github.com/browser-use/browser-use" className="text-amber-500 hover:text-amber-400 underline">Browser-Use</a> framework, 
                we've achieved 3-5x faster task completion, a dramatically simpler codebase, and rock-solid reliability.
              </p>

              <div className="bg-green-900/10 border-l-4 border-green-600 p-6 my-8 rounded-r-lg">
                <p className="text-green-400 font-semibold mb-2">✨ What's New</p>
                <ul className="text-stone-400 text-sm space-y-2 list-none pl-0">
                  <li>⚡ <strong className="text-stone-300">3-5x faster</strong> browser task completion</li>
                  <li>🧹 <strong className="text-stone-300">Removed 2000+ lines</strong> of complex browser control code</li>
                  <li>🛡️ <strong className="text-stone-300">Built-in retry logic</strong> and error recovery</li>
                  <li>🧠 <strong className="text-stone-300">Gemini 2.0 Flash</strong> optimized for speed</li>
                </ul>
              </div>

              <h2 className="text-3xl font-bold text-stone-100 mt-12 mb-4">Why We Migrated</h2>
              <p className="text-stone-400 mb-4">
                Weaszel 1.x was built on Google's Gemini Computer Use API with manual Playwright browser control. 
                While functional, it had some pain points:
              </p>
              <ul className="list-disc list-inside text-stone-400 space-y-2 mb-6">
                <li><strong className="text-stone-300">Complex codebase:</strong> Over 2000 lines of manual coordinate denormalization, screenshot handling, and action dispatching</li>
                <li><strong className="text-stone-300">Slower execution:</strong> Manual loops meant more round-trips to the LLM</li>
                <li><strong className="text-stone-300">Fragile error handling:</strong> Recovery logic had to be manually implemented for every edge case</li>
                <li><strong className="text-stone-300">Maintenance burden:</strong> Every browser update or Playwright change required careful testing</li>
              </ul>

              <p className="text-stone-400 mb-6">
                When we discovered Browser-Use—an open-source framework specifically designed for AI browser agents—we knew it was the right move.
              </p>

              <h2 className="text-3xl font-bold text-stone-100 mt-12 mb-4">What is Browser-Use?</h2>
              <p className="text-stone-400 mb-4">
                <a href="https://github.com/browser-use/browser-use" className="text-amber-500 hover:text-amber-400 underline">Browser-Use</a> is 
                a modern framework built specifically for AI agents to control web browsers. It handles all the heavy lifting:
              </p>
              <ul className="list-disc list-inside text-stone-400 space-y-2 mb-6">
                <li>Intelligent browser state management</li>
                <li>Automatic screenshot optimization</li>
                <li>Built-in retry logic for flaky web elements</li>
                <li>Native support for modern LLMs (Gemini, GPT-4, Claude)</li>
                <li>Production-ready error handling</li>
              </ul>

              <p className="text-stone-400 mb-6">
                Instead of re-inventing the wheel, we can now focus on what makes Weaszel unique: being your cozy AI companion.
              </p>

              <h2 className="text-3xl font-bold text-stone-100 mt-12 mb-4">The Numbers Don't Lie</h2>
              <div className="bg-[#0c0a09] border border-stone-800 rounded-lg p-6 mb-6">
                <div className="grid md:grid-cols-3 gap-6 text-center">
                  <div>
                    <div className="text-4xl font-bold text-green-400 mb-2">3-5x</div>
                    <div className="text-sm text-stone-500">Faster Task Completion</div>
                  </div>
                  <div>
                    <div className="text-4xl font-bold text-amber-400 mb-2">-2000</div>
                    <div className="text-sm text-stone-500">Lines of Code Removed</div>
                  </div>
                  <div>
                    <div className="text-4xl font-bold text-blue-400 mb-2">100%</div>
                    <div className="text-sm text-stone-500">Feature Parity</div>
                  </div>
                </div>
              </div>

              <h2 className="text-3xl font-bold text-stone-100 mt-12 mb-4">Technical Deep Dive</h2>
              
              <h3 className="text-2xl font-bold text-stone-200 mt-8 mb-3">Architecture Before (v1.x)</h3>
              <div className="bg-black/50 rounded-lg p-6 mb-6 font-mono text-sm border border-stone-800 overflow-x-auto">
                <pre className="text-stone-400">{`User Query
   ↓
weasel.py (Main Loop)
   ↓
BrowserAgent (Manual Loop)
   ↓
├─ Screenshot Capture
├─ Coordinate Normalization
├─ Gemini API Call
├─ Response Parsing
├─ Action Dispatch
└─ PlaywrightComputer (Manual Browser Control)
   ↓
Repeat until done`}</pre>
              </div>

              <h3 className="text-2xl font-bold text-stone-200 mt-8 mb-3">Architecture Now (v2.0)</h3>
              <div className="bg-black/50 rounded-lg p-6 mb-6 font-mono text-sm border border-stone-800 overflow-x-auto">
                <pre className="text-green-400">{`User Query
   ↓
weasel.py (Routing)
   ↓
BrowserAgent (Browser-Use Wrapper)
   ↓
browser-use.Agent
   ↓
✨ Automatic everything ✨
   ↓
Result`}</pre>
              </div>

              <p className="text-stone-400 mb-6">
                The new architecture is dramatically simpler. Browser-Use handles state management, retries, and browser orchestration internally, 
                letting us focus on user experience instead of browser internals.
              </p>

              <h2 className="text-3xl font-bold text-stone-100 mt-12 mb-4">What About Desktop Control?</h2>
              <p className="text-stone-400 mb-4">
                We've kept the experimental desktop control feature available as a legacy fallback for users who need it, 
                but we now recommend sticking with the default browser mode for the best experience.
              </p>
              <p className="text-stone-400 mb-6">
                Browser-Use is laser-focused on web automation, and that's where Weaszel 2.0 shines brightest.
              </p>

              <h2 className="text-3xl font-bold text-stone-100 mt-12 mb-4">Upgrading to 2.0</h2>
              <p className="text-stone-400 mb-4">
                The upgrade is seamless. Just run the installer again to update everything automatically:
              </p>
              <div className="bg-black/50 rounded-lg p-6 mb-6 font-mono text-sm border border-stone-800">
                <code className="text-amber-400">curl -sL https://weaszel.com/install.sh | bash<br/>
weaszel</code>
              </div>
              <p className="text-stone-400 mb-6">
                Or if you prefer manual updates, just pull the latest changes. Then simply type <code className="text-amber-400">weaszel</code> as usual.
              </p>

              <h2 className="text-3xl font-bold text-stone-100 mt-12 mb-4">Looking Ahead</h2>
              <p className="text-stone-400 mb-6">
                This migration isn't just about performance—it's about building on a solid foundation. With Browser-Use handling the browser layer, 
                we can now focus on:
              </p>
              <ul className="list-disc list-inside text-stone-400 space-y-2 mb-6">
                <li>Custom workflows for job applications and research</li>
                <li>Multi-step automation chains</li>
                <li>Better data extraction and summarization</li>
                <li>A friendlier UX with richer feedback</li>
              </ul>

              <div className="bg-amber-900/10 border-l-4 border-amber-600 p-6 my-8 rounded-r-lg">
                <p className="text-amber-500 font-semibold mb-2">🦊 Thanks for Being Here</p>
                <p className="text-stone-400">
                  We're incredibly excited about this release. Weaszel is faster, simpler, and more reliable than ever. 
                  Give it a try, and let us know what you think!
                </p>
              </div>

              <div className="mt-12 pt-8 border-t border-stone-800">
                <p className="text-stone-500 text-sm">
                  Questions or feedback? Reach out on <a href="https://github.com/smammadov1994/Weaszel" className="text-amber-500 hover:text-amber-400 underline">GitHub</a>.
                </p>
              </div>
            </div>
          </article>
        </div>
      </div>
    </div>
  );
}
