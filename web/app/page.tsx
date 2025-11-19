'use client';

import React, { useState } from 'react';
import { Terminal, Zap, Globe, Coffee, Download, ChevronRight, Copy, Check, Search, ShoppingBag } from 'lucide-react';
import { motion } from 'framer-motion';

export default function LandingPage() {
  const [copied, setCopied] = useState(false);

  const copyCommand = () => {
    navigator.clipboard.writeText('curl -sL https://weaszel.com/install.sh | bash');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const weaselAscii = `
⠀⠀⠀⠀⠀⠀⠀⠀⣠⡶⣛⣉⣙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣾⠋⠁⠀⠀⠀⠑⣿⣆⠀⢠⡤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡇⠀⡴⠋⠑⣄⢤⡤⠧⣤⣬⣦⢤⣵⣤⣀⣠⢴⣶⡶⠶⠿⠿⣶⣶⣤⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⣘⣤⠿⠛⠛⠅⠀⠀⠀⠈⠉⠙⢿⣧⡀⠀⣀⣀⣀⠀⠙⢿⢹⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡇⠀⣲⡟⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⡿⡍⠁⠀⠙⡗⠀⠈⡇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡇⠊⣷⠋⠰⠒⠄⠀⠀⠀⠀⠀⠀⠀⡖⡆⠀⠀⠀⠀⠈⢇⢧⠀⠀⠀⠁⠀⢸⡇⠀⠀
⠀⠀⠀⠀⠀⠀⠘⡇⡼⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡎⣾⣛⠀⠀⢀⡟⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣯⠇⡴⣫⣳⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡤⣄⠀⠀⠀⠀⠀⡇⡟⠃⠀⠀⡾⠃⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡞⡎⣸⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣯⣷⣷⠀⠀⠀⠀⡇⡧⠤⠶⠛⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢰⢱⠃⡿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⣼⡟⡷⣷⣯⡇⡇⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⡤⣞⣉⡍⢏⡼⠀⠘⠷⠃⠁⣀⣀⣀⠀⠀⠀⠀⣇⢿⣿⡿⢼⡾⠁⠀⠀⠀⣿⣒⡲⠶⠦⠀⠀⠀⠀⠀
⠉⢁⠖⠉⢀⡜⣷⠀⠀⠀⠀⠀⠈⠉⠉⠀⠀⠀⠀⠛⠉⠙⠉⠉⠀⠀⠀⠀⣾⠳⢤⣄⠑⠦⡀⠀⠀⠀⠀
⠀⣎⡤⢺⠋⠀⠘⡧⡀⠀⠸⠤⠞⢧⣀⡼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠟⡜⢹⡧⢄⡘⢌⠑⠦⣳⡀⠀
⠘⠁⢠⠃⠀⡠⠔⠉⠻⢷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡤⠖⠡⠖⡡⠊⣿⠀⠀⠈⠳⠀⠀⠁⠀⠀
⠀⠀⠘⠛⠉⠀⠀⠀⠀⠀⠈⣷⣍⠛⠛⠭⠭⠭⠭⠟⢋⡥⠞⠁⠀⠀⠉⠀⠀⣷⣇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣯⠢⣝⠒⠒⠒⠒⡉⠉⠀⠀⠀⠀⠀⠀⠀⢀⠎⠀⠀⡏⢧⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡟⢆⡀⠀⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠊⠁⠀⠀⠘⣼⡆⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⣽⠇⠓⠤⠥⠭⠭⠭⠀⠀⠀⠀⠀⠀⠀⡆⠀⠀⠀⠀⡤⠊⢱⡘⡄⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠁⣿⡶⣒⣶⡀⠀⠀⣠⡶⠶⠒⠒⠖⠋⠀⠀⠀⡀⠀⠀⠀⣀⠔⠻⡼⡀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡰⠁⣼⠃⠚⢁⣼⡇⠀⢰⣇⡒⠒⠂⠀⠀⠀⠀⠀⠀⣇⠀⠀⠀⠁⠀⠀⣸⣿⡀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠁⠀⠀⠈⣝⠇⠀⠀⢳⡄⠉⠁⠀⠀⠀⢀⡴⠓⠋⠀⠀⠀⠀⠀⠀⠀⠀⠘⣆
⠀⠀⠀⠀⠀⠀⠀⠀⠧⣀⣀⡠⠶⠋⠁⠀⠀⠀⠀⠉⠉⠙⠛⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`;

  return (
    <div className="min-h-screen bg-[#1c1917] text-[#e7e5e4] font-mono selection:bg-amber-900 selection:text-white">
      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 border-b border-stone-800 bg-[#1c1917]/90 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 text-amber-600">
            <Terminal className="w-6 h-6" />
            <span className="font-bold text-xl tracking-tighter text-stone-200">WEASZEL</span>
          </div>
          
          <div className="flex items-center gap-6">
             <div className="hidden md:flex gap-6 text-sm text-stone-400">
                <a href="#features" className="hover:text-amber-500 transition-colors">Features</a>
                <a href="/blog" className="hover:text-amber-500 transition-colors">Blog</a>
                <a href="#install" className="hover:text-amber-500 transition-colors">Install</a>
             </div>
             <a 
               href="https://buymeacoffee.com/smammadov94" 
               target="_blank"
               className="flex items-center gap-2 bg-[#3f3026] hover:bg-[#554134] text-amber-100 px-4 py-2 rounded-full text-sm font-bold transition-all border border-amber-900/30"
             >
               <Coffee className="w-4 h-4 text-amber-400" />
               Buy me a coffee
             </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-block px-3 py-1 border border-amber-800/30 rounded-full bg-amber-900/10 text-amber-500 text-xs mb-6 font-bold">
              🌰 v1.0.0 Released
            </div>
            <h1 className="text-5xl md:text-7xl font-bold leading-tight mb-6 text-stone-100">
              Your Cozy <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-500 to-orange-600">AI Companion.</span>
            </h1>
            <p className="text-xl text-stone-400 mb-8 max-w-lg">
              Weaszel lives in your terminal and surfs the web for you. From research to shopping, it handles the boring stuff so you can relax.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <a href="#install" className="flex items-center justify-center gap-2 bg-amber-700 hover:bg-amber-600 text-white px-8 py-4 rounded-lg font-bold transition-all shadow-lg shadow-amber-900/20">
                <Download className="w-5 h-5" />
                Get Weaszel
              </a>
              <a href="https://github.com/smammadov94/job-weasel" target="_blank" className="flex items-center justify-center gap-2 border border-stone-700 hover:bg-stone-800 text-stone-300 px-8 py-4 rounded-lg font-bold transition-all">
                View Source
              </a>
            </div>
          </motion.div>

          {/* Terminal Demo */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="relative"
          >
            <div className="absolute -inset-1 bg-gradient-to-r from-amber-700 to-orange-800 rounded-xl blur opacity-20"></div>
            <div className="relative bg-[#0c0a09] border border-stone-800 rounded-xl overflow-hidden shadow-2xl">
              <div className="flex items-center gap-2 px-4 py-3 border-b border-stone-800 bg-[#1c1917]">
                <div className="w-3 h-3 rounded-full bg-[#ef4444]"></div>
                <div className="w-3 h-3 rounded-full bg-[#eab308]"></div>
                <div className="w-3 h-3 rounded-full bg-[#22c55e]"></div>
                <div className="ml-4 text-xs text-stone-500 font-mono">weaszel — -zsh — 80x24</div>
              </div>
              <div className="p-6 font-mono text-sm md:text-base space-y-2 h-[450px] overflow-y-auto scrollbar-hide">
                <div className="text-stone-500">$ weaszel</div>
                <div className="text-amber-600 font-bold text-[8px] leading-[8px] md:text-[10px] md:leading-[10px] overflow-hidden whitespace-pre">
                  {weaselAscii}
                </div>
                <div className="text-stone-400 italic mt-4">🦊 Your Cozy AI Companion for the Web.</div>
                <br />
                <div className="text-stone-300">What would you like me to do?</div>
                <div className="text-amber-500">{`> Find a mechanical keyboard on Amazon`}</div>
                <div className="text-stone-500">Thinking...</div>
                <div className="text-blue-400">Action: Navigate to Amazon.com</div>
                <div className="text-blue-400">Action: Search "Mechanical Keyboard"</div>
                <div className="text-green-500">Found 5 great options! Here is the top pick: Keychron K2 ⌨️</div>
                <br />
                <div className="text-stone-300">What's next?</div>
                <div className="text-amber-500">{`> Check the weather in Tokyo`}</div>
                <div className="text-blue-400">Action: Search Google Weather</div>
                <div className="text-green-500">It's currently 18°C and Cloudy in Tokyo ☁️</div>
                <div className="animate-pulse text-amber-500">_</div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 border-t border-stone-800 bg-[#1c1917]/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-8 rounded-2xl bg-[#0c0a09] border border-stone-800 hover:border-amber-700/50 transition-colors group">
              <div className="w-12 h-12 bg-amber-900/20 rounded-lg flex items-center justify-center mb-6 group-hover:bg-amber-900/30 transition-colors">
                <Globe className="w-6 h-6 text-amber-600" />
              </div>
              <h3 className="text-xl font-bold mb-4 text-stone-200">Web Automation</h3>
              <p className="text-stone-500">Weaszel can browse any website just like you do. It clicks, types, and scrolls to get things done.</p>
            </div>
            <div className="p-8 rounded-2xl bg-[#0c0a09] border border-stone-800 hover:border-orange-700/50 transition-colors group">
              <div className="w-12 h-12 bg-orange-900/20 rounded-lg flex items-center justify-center mb-6 group-hover:bg-orange-900/30 transition-colors">
                <Search className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="text-xl font-bold mb-4 text-stone-200">Deep Research</h3>
              <p className="text-stone-500">Need to find something specific? Weaszel digs deep, reads content, and summarizes findings for you.</p>
            </div>
            <div className="p-8 rounded-2xl bg-[#0c0a09] border border-stone-800 hover:border-green-700/50 transition-colors group">
              <div className="w-12 h-12 bg-green-900/20 rounded-lg flex items-center justify-center mb-6 group-hover:bg-green-900/30 transition-colors">
                <ShoppingBag className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-xl font-bold mb-4 text-stone-200">Shopping Assistant</h3>
              <p className="text-stone-500">Find the best deals, compare prices, and even fill out checkout forms automatically.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Install Section */}
      <section id="install" className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-8 text-stone-100">Invite Weaszel into your terminal.</h2>
          <p className="text-stone-400 mb-12">One command to get started.</p>
          
          <div className="bg-[#0c0a09] border border-stone-800 rounded-xl p-6 flex items-center justify-between max-w-2xl mx-auto group hover:border-amber-700/50 transition-all shadow-2xl">
            <code className="text-amber-500 font-mono text-sm md:text-base">
              curl -sL https://weaszel.com/install.sh | bash
            </code>
            <button 
              onClick={copyCommand}
              className="ml-4 p-2 hover:bg-stone-800 rounded-lg transition-colors text-stone-500 hover:text-stone-300"
            >
              {copied ? <Check className="w-5 h-5 text-green-500" /> : <Copy className="w-5 h-5" />}
            </button>
          </div>
          
          <div className="mt-12 flex flex-col items-center gap-4">
            <p className="text-sm text-stone-500">Requires Python 3.10+ and Chrome</p>
            <a href="https://aistudio.google.com/app/apikey" target="_blank" className="text-amber-600 hover:text-amber-500 hover:underline text-sm transition-colors">
              Get your Gemini API Key here →
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-stone-800 bg-[#1c1917]">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center text-stone-500 text-sm">
          <div>© 2025 Weaszel. Crafted with 🌰 by Seymur.</div>
          <div className="flex gap-6 mt-4 md:mt-0">
            <a href="#" className="hover:text-amber-500 transition-colors">Twitter</a>
            <a href="#" className="hover:text-amber-500 transition-colors">GitHub</a>
            <a href="mailto:smammadov94@gmail.com" className="hover:text-amber-500 transition-colors">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
