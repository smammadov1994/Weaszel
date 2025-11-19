'use client';

import React from 'react';
import { Terminal, ArrowLeft, DollarSign, Shield, Zap, XCircle, CheckCircle } from 'lucide-react';
import Link from 'next/link';

export default function BlogPage() {
  return (
    <div className="min-h-screen bg-[#1c1917] text-[#e7e5e4] font-mono selection:bg-amber-900 selection:text-white">
      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 border-b border-stone-800 bg-[#1c1917]/90 backdrop-blur-md">
        <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-amber-600 hover:text-amber-500 transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span className="font-bold">Back to Weaszel</span>
          </Link>
          <div className="flex items-center gap-2 text-stone-500 text-sm">
            <span>Nov 19, 2025</span>
            <span>•</span>
            <span>5 min read</span>
          </div>
        </div>
      </nav>

      {/* Content */}
      <article className="pt-32 pb-20 px-6 max-w-3xl mx-auto">
        <div className="mb-12">
          <div className="inline-block px-3 py-1 border border-amber-800/30 rounded-full bg-amber-900/10 text-amber-500 text-xs mb-6 font-bold">
            Opinion
          </div>
          <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6 text-stone-100">
            Why "Agents" Are Broken: <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-500 to-orange-600">The Case for Owning Your AI.</span>
          </h1>
          <p className="text-xl text-stone-400 leading-relaxed">
            Big tech wants you to rent their agents for $20/month. Weaszel proves there's a better, cheaper, and more powerful way.
          </p>
        </div>

        <div className="prose prose-invert prose-stone max-w-none">
          <p>
            The promise of AI agents is simple: an assistant that does the work for you. It books flights, applies for jobs, and buys groceries while you sleep.
          </p>
          <p>
            But the reality of today's "premium" agents—like OpenAI's $20/month offering or Anthropic's Claude—is far from that dream. They are walled gardens, expensive toys, and fundamentally limited by their creators.
          </p>

          <h2 className="text-2xl font-bold text-stone-100 mt-12 mb-6">The $20/Month "Beta Test"</h2>
          <p>
            Let's look at OpenAI's recent "Agent" launch. For a monthly subscription, you get access to a tool that claims to browse the web. In reality?
          </p>
          <ul className="space-y-4 my-8">
            <li className="flex items-start gap-3">
              <XCircle className="w-6 h-6 text-red-500 shrink-0 mt-1" />
              <div>
                <strong className="text-stone-200">Blocked Everywhere:</strong> Amazon, Walmart, Target, and Best Buy all block it. It can't shop for you if it can't get in the door.
              </div>
            </li>
            <li className="flex items-start gap-3">
              <XCircle className="w-6 h-6 text-red-500 shrink-0 mt-1" />
              <div>
                <strong className="text-stone-200">No Real Action:</strong> It can't actually book flights or make reservations. It's a "look but don't touch" browser.
              </div>
            </li>
            <li className="flex items-start gap-3">
              <XCircle className="w-6 h-6 text-red-500 shrink-0 mt-1" />
              <div>
                <strong className="text-stone-200">Opaque Token Burning:</strong> It spins its wheels for 20 minutes, burning invisible credits, only to fail silently.
              </div>
            </li>
          </ul>

          <h2 className="text-2xl font-bold text-stone-100 mt-12 mb-6">The Cost of Claude</h2>
          <p>
            Anthropic's Claude 3.5 Sonnet is incredible, but it comes with a steep price tag. Running an agent loop with Claude can cost upwards of $3 per million input tokens.
          </p>
          <p>
            For a single complex task that requires 50 steps and constant screen reading, you could burn through $5-$10 in a single afternoon. It's powerful, but it's not sustainable for daily automation unless you have a corporate budget.
          </p>

          <div className="my-12 p-8 bg-[#0c0a09] border border-amber-900/30 rounded-2xl">
            <h3 className="text-xl font-bold text-amber-500 mb-4">Enter Weaszel: The Freedom to Choose</h3>
            <p className="mb-6">
              Weaszel takes a different approach. Instead of renting a black box, you <strong>own the agent</strong>. It runs on your machine, in your terminal, using your browser.
            </p>
            <div className="grid gap-4">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span><strong>Powered by Gemini 2.5:</strong> Google's latest Computer Use model is significantly cheaper and designed specifically for this.</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span><strong>Stealth Mode:</strong> Because it uses <em>your</em> Chrome browser, it bypasses Cloudflare and anti-bot checks naturally. You're already logged in.</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span><strong>Full Control:</strong> No hidden limits. No "safety" blocks preventing you from booking a flight. If you can do it, Weaszel can do it.</span>
              </div>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-stone-100 mt-12 mb-6">How It Works</h2>
          <p>
            Weaszel leverages the new <strong>Gemini 2.5 Computer Use Preview</strong>. This model is trained to "see" screens just like a human does.
          </p>
          <p>
            When you give Weaszel a command, it:
          </p>
          <ol className="list-decimal list-inside space-y-2 ml-4 text-stone-400">
            <li>Takes a screenshot of your browser.</li>
            <li>Sends it to Gemini to analyze.</li>
            <li>Receives coordinates for where to click or what to type.</li>
            <li>Executes the action using Playwright.</li>
            <li>Repeats the loop until the job is done.</li>
          </ol>

          <p className="mt-8">
            This "Human-in-the-Loop" architecture is the future. You aren't relying on an API to integrate with Amazon; you're relying on a visual intelligence that navigates Amazon just like you would.
          </p>

          <h2 className="text-2xl font-bold text-stone-100 mt-12 mb-6">Stop Renting. Start Owning.</h2>
          <p>
            The era of paying $20/month for a broken promise is over. Download Weaszel, get your own API key (pay only for what you use), and unleash a true agent into your terminal.
          </p>
          
          <div className="mt-12 pt-8 border-t border-stone-800">
            <Link href="/#install" className="inline-flex items-center justify-center gap-2 bg-amber-700 hover:bg-amber-600 text-white px-8 py-4 rounded-lg font-bold transition-all w-full md:w-auto">
              <Terminal className="w-5 h-5" />
              Install Weaszel Now
            </Link>
          </div>
        </div>
      </article>
    </div>
  );
}
