import Link from "next/link";

export default function Hero() {
  return (
    <section
      id="platform"
      className="relative overflow-hidden rounded-2xl bg-brand text-white shadow-xl"
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_-20%,rgba(255,255,255,0.1),transparent)]" />

      <div className="relative grid lg:grid-cols-[1.5fr_1fr] gap-12 items-center px-8 py-20 lg:py-24 lg:px-14">
        {/* Copy */}
        <div className="max-w-2xl">
          <p className="text-[11px] font-bold tracking-[0.2em] uppercase text-brand-accent mb-6">
            Institutional Research Quality Control
          </p>
          <h1 className="text-4xl sm:text-5xl lg:text-[3.25rem] font-serif font-bold leading-[1.15] tracking-tight">
            Elevate your manuscript status with precision review.
          </h1>
          <p className="mt-8 text-blue-100/90 text-lg lg:text-xl leading-relaxed max-w-xl font-medium">
            A centralized infrastructure for universities and labs to standardize
            submission readiness and accelerate publication cycles.
          </p>

          <div className="mt-10 flex flex-wrap gap-4">
            <Link
              href="/student"
              className="px-7 py-3.5 rounded-lg bg-white text-brand font-bold text-sm hover:bg-gray-50 transition-all shadow-md"
            >
              Student Dashboard
            </Link>
            <Link
              href="/professor"
              className="px-7 py-3.5 rounded-lg border border-white/40 text-white font-bold text-sm hover:bg-white/10 transition-all shadow-sm"
            >
              Professor Dashboard
            </Link>
          </div>

          <p className="mt-8 text-xs text-blue-200/60 font-medium">
            Enterprise-grade quality control for academic excellence.
          </p>
        </div>

        {/* KPI card */}
        <div className="hidden lg:block">
          <div className="bg-white/[0.03] border border-white/10 backdrop-blur-md rounded-2xl p-8 shadow-2xl">
            <p className="text-[10px] font-bold tracking-[0.15em] uppercase text-brand-accent mb-6">
              Platform Metrics
            </p>
            <div className="grid grid-cols-2 gap-8">
              {[
                ["30+", "Quality Checks"],
                ["Instant", "Analysis"],
                ["PDF", "Native Support"],
                ["Global", "Standards"],
              ].map(([val, label]) => (
                <div key={label}>
                  <p className="text-3xl font-serif font-bold text-white">{val}</p>
                  <p className="text-[11px] text-blue-200/70 mt-1 uppercase tracking-wider font-bold">{label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
