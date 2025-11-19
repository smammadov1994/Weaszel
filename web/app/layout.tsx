import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "Weaszel | The AI Automation Agent for Computer Vision & Web Tasks",
  description: "Weaszel is the ultimate AI automation tool. Powered by Gemini Computer Vision, it automates browser tasks, job applications, and data entry. The best open-source alternative to expensive agents.",
  keywords: [
    "AI automation",
    "computer vision",
    "browser automation",
    "autonomous agent",
    "Gemini 2.5",
    "computer use model",
    "python agent",
    "web scraper",
    "job application bot",
    "selenium alternative",
    "playwright automation",
    "AI assistant",
    "terminal agent"
  ],
  openGraph: {
    title: "Weaszel | AI Automation & Computer Vision Agent",
    description: "Stop renting AI. Own your agent. Weaszel uses advanced Computer Vision to automate the web for you.",
    url: "https://weazel.com",
    siteName: "Weaszel",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Weaszel | AI Automation Agent",
    description: "Automate the web with Computer Vision. The cozy, open-source AI agent.",
  },
  alternates: {
    canonical: "https://weazel.com",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${inter.variable} ${mono.variable} font-sans antialiased bg-[#1c1917] text-[#e7e5e4]`}>
        {children}
      </body>
    </html>
  );
}
