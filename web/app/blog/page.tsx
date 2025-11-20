import { Metadata } from 'next';
import Link from 'next/link';

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
    badgeColor: 'purple',
  },
];

export default function BlogIndexPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-black to-purple-900">
      <div className="container mx-auto px-6 py-20">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <h1 className="text-5xl font-bold text-white mb-4">
              📝 Blog
            </h1>
            <p className="text-xl text-purple-300">
              Thoughts, updates, and insights about AI agents
            </p>
          </div>

          {/* Blog Posts */}
          <div className="space-y-6">
            {blogPosts.map((post) => (
              <Link
                key={post.slug}
                href={`/blog/${post.slug}`}
                className="block bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-purple-500/30 hover:border-purple-500/60 transition-all hover:scale-[1.02] group"
              >
                <div className="flex items-start justify-between mb-4">
                  <span
                    className={`px-4 py-2 rounded-full text-sm font-semibold ${
                      post.badgeColor === 'yellow'
                        ? 'bg-yellow-500/20 text-yellow-300'
                        : 'bg-purple-500/20 text-purple-300'
                    }`}
                  >
                    {post.badge}
                  </span>
                  <span className="text-purple-300 text-sm">{post.date}</span>
                </div>
                <h2 className="text-2xl font-bold text-white mb-3 group-hover:text-purple-300 transition-colors">
                  {post.title}
                </h2>
                <p className="text-gray-300 mb-4">{post.description}</p>
                <span className="text-purple-400 group-hover:text-purple-300 transition-colors inline-flex items-center gap-2">
                  Read more →
                </span>
              </Link>
            ))}
          </div>

          {/* Back to Home */}
          <div className="mt-12 text-center">
            <Link
              href="/"
              className="inline-flex items-center text-purple-300 hover:text-purple-200 transition-colors"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
