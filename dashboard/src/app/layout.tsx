import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smart Study Monitor — AI Focus Intelligence",
  description: "Real-time AI behavioral monitor, focus scoring, and study analytics platform."
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-zinc-950 text-zinc-100 min-h-screen antialiased flex flex-col">
        {/* Navigation Bar */}
        <header className="border-b border-zinc-800/80 bg-zinc-900/60 backdrop-blur sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-emerald-400 flex items-center justify-center text-lg font-black text-white shadow-lg shadow-indigo-500/20">
                S
              </span>
              <div>
                <h1 className="text-sm font-bold tracking-tight text-white uppercase">
                  Smart Study Monitor
                </h1>
                <span className="text-[10px] text-zinc-400 font-mono block">
                  AI BEHAVIORAL INTELLIGENCE v12.0
                </span>
              </div>
            </div>

            <nav className="flex items-center gap-6 text-sm font-medium">
              <Link
                href="/"
                className="text-zinc-300 hover:text-white transition px-3 py-1.5 rounded-lg hover:bg-zinc-800/60"
              >
                Live Monitor
              </Link>
              <Link
                href="/history"
                className="text-zinc-400 hover:text-white transition px-3 py-1.5 rounded-lg hover:bg-zinc-800/60"
              >
                Study History
              </Link>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        {/* Footer */}
        <footer className="border-t border-zinc-900 py-6 text-center text-xs text-zinc-400">
          Smart Study Monitor &copy; 2026 &bull; Privacy-first edge AI telemetry
        </footer>
      </body>
    </html>
  );
}
