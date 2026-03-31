import Link from "next/link";

const roles = [
  {
    tag: "Student Dashboard",
    title: "Draft Quality Workspace",
    desc: "Upload papers, run analysis, and review section-wise quality findings in a clean interface.",
    href: "/student",
    cta: "Launch workspace",
  },
  {
    tag: "Professor Dashboard",
    title: "Governance & Format Control",
    desc: "Create approved formats, enforce required sections, and guide consistent submissions.",
    href: "/professor",
    cta: "Launch workspace",
  },
];

export default function Roles() {
  return (
    <section id="roles" className="bg-white border border-line rounded-2xl p-8 lg:p-10 shadow-sm">
      <div className="mb-10 text-center max-w-2xl mx-auto">
        <h2 className="text-2xl sm:text-3xl font-serif font-bold text-ink">Specialized Workspaces</h2>
        <p className="text-[15px] text-ink-soft mt-3 font-medium">
          Focused environments tailored for research excellence and institutional governance.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 gap-6">
        {roles.map((r) => (
          <Link
            key={r.tag}
            href={r.href}
            className="group block border border-line rounded-xl p-8 bg-panel-muted hover:border-brand/20 hover:bg-white hover:shadow-card transition-all duration-300"
          >
            <span className="inline-block text-[10px] font-bold uppercase tracking-[0.2em] text-brand bg-brand/5 px-3 py-1.5 rounded-full mb-6">
              {r.tag}
            </span>
            <h3 className="font-serif font-bold text-xl mb-3 text-ink group-hover:text-brand transition-colors">{r.title}</h3>
            <p className="text-[15px] text-ink-soft leading-relaxed mb-6 font-medium">{r.desc}</p>
            <span className="text-sm font-bold text-brand flex items-center gap-2">
              {r.cta} <span className="group-hover:translate-x-1 transition-transform">&rarr;</span>
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}
