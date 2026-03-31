import Link from "next/link";

export default function Footer({ showNav = true }) {
  return (
    <footer className="border-t border-line bg-panel-muted px-6 py-6 lg:py-8">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm">
        <div className="flex items-center gap-2">
          <p className="font-serif font-bold text-ink">FixMyPaper</p>
          <span className="text-[10px] text-ink-soft/50 font-bold uppercase tracking-widest hidden sm:inline">| Academic Quality Platform</span>
        </div>
        {showNav ? (
          <p className="text-ink-soft text-[13px] font-medium text-center sm:text-right max-w-xs">
            Professional manuscript quality infrastructure for academic
            institutions.
          </p>
        ) : (
          <nav className="flex gap-6 text-[13px] text-ink-soft font-medium">
            <Link href="/" className="hover:text-brand transition-colors">
              Home
            </Link>
            <Link href="/student" className="hover:text-brand transition-colors">
              Student
            </Link>
            <Link href="/professor" className="hover:text-brand transition-colors">
              Professor
            </Link>
          </nav>
        )}
      </div>
    </footer>
  );
}
