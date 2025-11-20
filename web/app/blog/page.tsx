import { Metadata } from 'next';
import Link from 'next/link';
import { ArrowLeft, Calendar } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Blog - Weaszel',
  description: 'Thoughts, updates, and insights about AI agents and automation',
};

const blogPosts = [
  {
    slug: 'desktop-control',
    title: 'Introducing Experimental Desktop Control',
    description: 'Learn about Weaszel\'s new experimental desktop control feature, its capabilities, limitations, and when to use it.',
    date: 'November 19, 2024',
    badge: '⚠️ Experimental',
    badgeColor: 'yellow',
  },
  {
    slug: 'why-agents-are-broken',
    title: 'Why "Agents" Are Broken: The Case for Owning Your AI',
    description: 'Big tech wants you to rent their agents for $20/month. Weaszel proves there\'s a better, cheaper, and more powerful way.',
    date: 'November 15, 2024',
    badge: 'Opinion',
    badgeColor: 'amber',
  },
];

export default function BlogIndexPage() {
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
              📝 Blog
            </h1>
            <p className="text-xl text-stone-400">
              Thoughts, updates, and insights about AI agents
            </p>
          </div>

          {/* Blog Posts */}
          <div className="space-y-6">
            {blogPosts.map((post) => (
              <Link
                key={post.slug}
                href={`/blog/${post.slug}`}
                className="block bg-[#0c0a09] border border-amber-900/30 rounded-2xl p-8 hover:border-amber-700/50 transition-all group"
              >
                <div className="flex items-start justify-between mb-4">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold ${
                      post.badgeColor === 'yellow'
                        ? 'bg-amber-900/20 text-amber-500 border border-amber-800/30'
                        : 'bg-amber-900/10 text-amber-500 border border-amber-800/30'
                    }`}
                  >
                    {post.badge}
                  </span>
                  <div className="flex items-center gap-2 text-stone-500 text-sm">
                    <Calendar className="w-4 h-4" />
                    <span>{post.date}</span>
                  </div>
                </div>
                <h2 className="text-2xl font-bold text-stone-100 mb-3 group-hover:text-amber-500 transition-colors">
                  {post.title}
                </h2>
                <p className="text-stone-400 mb-4 leading-relaxed">{post.description}</p>
                <span className="text-amber-500 group-hover:text-amber-400 transition-colors inline-flex items-center gap-2 text-sm font-bold">
                  Read more →
                </span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
