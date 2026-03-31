"use client";

import { getCheckNamesByCategory } from "@/lib/data";

const checksByCategory = getCheckNamesByCategory();

export default function Coverage() {
  return (
    <section id="coverage" className="bg-white border border-line rounded-2xl p-8 lg:p-10 shadow-sm">
      <div className="mb-10">
        <h2 className="text-2xl font-serif font-bold text-ink">Comprehensive Coverage</h2>
        <p className="text-[15px] text-ink-soft mt-2 font-medium">
          Multi-dimensional quality checks configured in the current institutional build.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(checksByCategory).map(([cat, names]) => (
          <div
            key={cat}
            className="border border-line bg-panel-muted rounded-xl p-6 hover:bg-white hover:shadow-sm transition-all duration-300"
          >
            <h4 className="text-xs font-bold uppercase tracking-wider text-brand mb-4">{cat}</h4>
            <div className="flex flex-wrap gap-2">
              {names.map((n) => (
                <span
                  key={n}
                  className="text-[11px] font-medium text-ink-soft bg-white border border-line rounded-full px-3 py-1 shadow-xs"
                >
                  {n}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
