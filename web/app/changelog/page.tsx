import { Metadata } from 'next';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Changelog - Weaszel',
  description: 'Latest updates, features, and improvements to Weaszel AI Agent',
};

export default function ChangelogPage() {
  return (
    <div className="min-h-screen bg-[#1c1917] text-[#e7e5e4] font-mono">
      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 border-b border-stone-800 bg-[#1c1917]/90 backdrop-blur-md">
        <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-amber-600 hover:text-amber-500 transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span className="font-bold">Back to Weaszel</span>
          </Link>
        </div>
      </nav>

      {/* Content */}
      <div className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-16">
            <h1 className="text-4xl md:text-5xl font-bold text-stone-100 mb-4">
              📝 Changelog
            </h1>
            <p className="text-xl text-stone-400">
              Track the evolution of Weaszel
            </p>
          </div>

          {/* Version 1.1.0 */}
          <div className="bg-[#0c0a09] border border-amber-900/30 rounded-2xl p-8 mb-8">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-4">
              <h2 className="text-3xl font-bold text-stone-100">v1.1.0</h2>
              <span className="px-4 py-2 bg-amber-900/20 text-amber-500 rounded-full text-sm font-bold border border-amber-800/30">
                ⚠️ Experimental
              </span>
            </div>
            <p className="text-stone-500 mb-6">Released: November 19, 2024</p>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold text-amber-500 mb-3">✨ New Features</h3>
                <ul className="space-y-2 text-stone-400">
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span><strong className="text-stone-300">Experimental Desktop Control:</strong> Weaszel can now control your local desktop applications (TextEdit, Finder, etc.) using macOS accessibility features</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span><strong className="text-stone-300">Smart Mode Selection:</strong> First-run experience now offers clear choice between Browser Automation (Recommended) and Full Desktop Control (Experimental)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span><strong className="text-stone-300">Query Validation:</strong> AI-powered input validation prevents the agent from acting on nonsensical or unclear commands</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span><strong className="text-stone-300">Intelligent Tool Selection:</strong> Gemini-powered decision engine determines whether tasks require browser or desktop actions</span>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-amber-500 mb-3">🔧 Improvements</h3>
                <ul className="space-y-2 text-stone-400">
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>Enhanced app focus reliability using AppleScript activation</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>Desktop navigation fallback: URLs now open in default browser even in desktop-only mode</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>Cleaned up dependency management and install script</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>Improved safety compliance with Gemini API protocols</span>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-amber-500 mb-3">🐛 Bug Fixes</h3>
                <ul className="space-y-2 text-stone-400">
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>Fixed environment variable scope issue causing NameError on startup</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>Resolved SDK warning about automatic function calling compatibility</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>Added missing <code className="bg-black/50 px-2 py-1 rounded text-amber-400">pillow</code> dependency to requirements.txt</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>Fixed desktop mode enforcement when feature is disabled</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* Version 1.0.0 */}
          <div className="bg-[#0c0a09] border border-stone-800 rounded-2xl p-8">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-4">
              <h2 className="text-3xl font-bold text-stone-100">v1.0.0</h2>
              <span className="px-4 py-2 bg-stone-800/50 text-stone-400 rounded-full text-sm font-bold">
                Stable
              </span>
            </div>
            <p className="text-stone-500 mb-6">Released: November 15, 2024</p>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold text-amber-500 mb-3">🎉 Initial Release</h3>
                <ul className="space-y-2 text-stone-400">
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>Browser automation powered by Gemini 2.5 Computer Use</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>Job application automation (LinkedIn, Indeed, etc.)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>Web research and data gathering</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>Persistent Chrome support for Cloudflare bypass</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-amber-500 mr-2">•</span>
                    <span>User profile management via user_data.md</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
