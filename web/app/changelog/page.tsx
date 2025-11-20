import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Changelog - Weaszel',
  description: 'Latest updates, features, and improvements to Weaszel AI Agent',
};

export default function ChangelogPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-black to-purple-900">
      <div className="container mx-auto px-6 py-20">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <h1 className="text-5xl font-bold text-white mb-4">
              📝 Changelog
            </h1>
            <p className="text-xl text-purple-300">
              Track the evolution of Weaszel
            </p>
          </div>

          {/* Version 1.1.0 */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 mb-8 border border-purple-500/30">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-3xl font-bold text-white">v1.1.0</h2>
              <span className="px-4 py-2 bg-yellow-500/20 text-yellow-300 rounded-full text-sm font-semibold">
                Experimental
              </span>
            </div>
            <p className="text-purple-300 mb-6">Released: November 19, 2024</p>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold text-green-400 mb-3">✨ New Features</h3>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span><strong>Experimental Desktop Control:</strong> Weaszel can now control your local desktop applications (TextEdit, Finder, etc.) using macOS accessibility features</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span><strong>Smart Mode Selection:</strong> First-run experience now offers clear choice between Browser Automation (Recommended) and Full Desktop Control (Experimental)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span><strong>Query Validation:</strong> AI-powered input validation prevents the agent from acting on nonsensical or unclear commands</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span><strong>Intelligent Tool Selection:</strong> Gemini-powered decision engine determines whether tasks require browser or desktop actions</span>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-blue-400 mb-3">🔧 Improvements</h3>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start">
                    <span className="text-blue-400 mr-2">•</span>
                    <span>Enhanced app focus reliability using AppleScript activation</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-400 mr-2">•</span>
                    <span>Desktop navigation fallback: URLs now open in default browser even in desktop-only mode</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-400 mr-2">•</span>
                    <span>Cleaned up dependency management and install script</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-400 mr-2">•</span>
                    <span>Improved safety compliance with Gemini API protocols</span>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-red-400 mb-3">🐛 Bug Fixes</h3>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>Fixed environment variable scope issue causing NameError on startup</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>Resolved SDK warning about automatic function calling compatibility</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>Added missing <code className="bg-black/30 px-2 py-1 rounded">pillow</code> dependency to requirements.txt</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-400 mr-2">•</span>
                    <span>Fixed desktop mode enforcement when feature is disabled</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* Version 1.0.0 */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-purple-500/30">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-3xl font-bold text-white">v1.0.0</h2>
              <span className="px-4 py-2 bg-green-500/20 text-green-300 rounded-full text-sm font-semibold">
                Stable
              </span>
            </div>
            <p className="text-purple-300 mb-6">Released: November 15, 2024</p>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold text-green-400 mb-3">🎉 Initial Release</h3>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span>Browser automation powered by Gemini 2.5 Computer Use</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span>Job application automation (LinkedIn, Indeed, etc.)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span>Web research and data gathering</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
                    <span>Persistent Chrome support for Cloudflare bypass</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-2">•</span>
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
