import Link from "next/link";
import Footer from "./Footer";

export default function DashboardShell({ caption, children }) {
  return (
    <div className="min-h-screen flex flex-col bg-panel-muted">
      {/* Top bar */}
      <header className="bg-brand text-white shadow-md border-b border-white/10">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-3">
            {/* <span className="w-10 h-10 rounded-lg bg-white/10 border border-white/20 text-white text-xs font-bold flex items-center justify-center">
              FP
            </span> */}
            <span>
              <span className="block text-[25px] font-serif font-bold leading-tight tracking-wide">FixMyPaper</span>
              <span className="block text-[10px] text-blue-200/70 font-bold uppercase tracking-widest mt-0.5">{caption}</span>
            </span>
          </Link>
          <Link
            href="/"
            className="text-sm font-bold text-blue-100 hover:text-white transition-colors flex items-center gap-2"
          >
            &larr; <span className="hidden sm:inline">Back to Home</span>
          </Link>
        </div>
      </header>

      {/* Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 flex flex-col gap-5">
        {children}
      </main>

      <Footer showNav={false} />
    </div>
  );
}
