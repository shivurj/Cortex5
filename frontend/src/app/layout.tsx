import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "Cortex5 | AI Hedge Fund",
  description: "Autonomous Agentic Trading System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${mono.variable} bg-slate-950 text-slate-200 font-sans antialiased`}>
        <div className="min-h-screen flex flex-col">
          <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
              <div className="flex items-center gap-8">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center font-bold text-slate-900">C5</div>
                  <span className="font-bold text-lg tracking-tight">CORTEX<span className="text-emerald-500">5</span></span>
                </div>
                <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
                  <a href="/" className="text-slate-300 hover:text-emerald-400 transition-colors">Dashboard</a>
                  <a href="/backtest" className="text-slate-300 hover:text-emerald-400 transition-colors">Backtest Engine</a>
                </nav>
              </div>
              <div className="flex items-center gap-4 text-sm font-mono text-slate-500">
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  SYSTEM ONLINE
                </span>
              </div>
            </div>
          </header>
          <main className="flex-1">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
