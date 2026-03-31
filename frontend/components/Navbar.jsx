import Link from "next/link";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-line">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3 group">
          {/* <span className="w-15 h-10 rounded-xl bg-brand text-white text-sm font-bold flex items-center justify-center shadow-sm">
            FixMyPaper
          </span> */}
          <span>
            <span className="block text-[25px] font-serif font-bold text-ink leading-tight">
              FixMyPaper
            </span>
            <span className="block text-[11px] text-ink-soft leading-tight font-medium">
              Research Quality Platform
            </span>
          </span>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          <a href="#platform" className="text-sm font-medium text-ink-soft hover:text-brand transition-colors">
            Platform
          </a>
          <a href="#capabilities" className="text-sm font-medium text-ink-soft hover:text-brand transition-colors">
            Capabilities
          </a>
          <a href="#roles" className="text-sm font-medium text-ink-soft hover:text-brand transition-colors">
            Dashboards
          </a>
          <a href="#coverage" className="text-sm font-medium text-ink-soft hover:text-brand transition-colors">
            Coverage
          </a>
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <Link
            href="/student"
            className="hidden sm:inline-flex px-5 py-2 text-sm font-semibold rounded-lg border border-line bg-white text-ink hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm"
          >
            Student
          </Link>
          <Link
            href="/professor"
            className="px-5 py-2 text-sm font-semibold rounded-lg bg-brand text-white hover:bg-brand-dark transition-all shadow-sm"
          >
            Professor
          </Link>
        </div>
      </div>
    </header>
  );
}
