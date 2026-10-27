import Link from 'next/link'
import { ArrowLeft, ArrowUpRight, BookOpen, BriefcaseBusiness, Cloud, Compass, Wrench } from 'lucide-react'

const paths = [
  { slug: 'first-steps-ai-ml', id: 'fundamentals', number: '01', label: 'For curious beginners', title: 'First steps into AI / ML', description: 'Build a plain-language mental model of machine learning, then try the ideas hands-on.', icon: BookOpen, tone: 'bg-[#f5cb54]', stages: '3 stages', outcome: 'A clear technical foundation' },
  { slug: 'backend-foundations', id: 'backend', number: '02', label: 'For future builders', title: 'Backend development foundations', description: 'Learn how applications move data, serve requests, and stay reliable behind the interface.', icon: Wrench, tone: 'bg-[#bde8d4]', stages: '3 stages', outcome: 'A working service blueprint' },
  { slug: 'cloud-computing', id: 'cloud', number: '03', label: 'For systems thinkers', title: 'Cloud computing fundamentals', description: 'Understand the building blocks behind modern apps: compute, storage, networks, and deployment.', icon: Cloud, tone: 'bg-[#e9d8ff]', stages: '3 stages', outcome: 'A cloud vocabulary you can use' },
  { slug: 'first-practical-project', id: 'projects', number: '04', label: 'For learning by doing', title: 'Build a first practical project', description: 'Go from a small idea to a finished project with a scope you can actually complete.', icon: Compass, tone: 'bg-[#ef6c4d] text-white', stages: '3 stages', outcome: 'Something real to show' },
  { slug: 'technical-internship-prep', id: 'career', number: '05', label: 'For early-career learners', title: 'Prepare for technical internships', description: 'Turn your foundations into evidence: projects, technical fluency, and a story about how you learn.', icon: BriefcaseBusiness, tone: 'bg-[#20221f] text-[#f5f4ef]', stages: '3 stages', outcome: 'A stronger application story' },
]

export default function PathsPage() {
  return (
    <main className="min-h-screen bg-[#f5f4ef] text-[#20221f]">
      {/* HEADER */}
      <header className="mx-auto flex max-w-7xl items-center justify-between px-5 py-6 lg:px-10 border-b border-[#20221f]/10 sticky top-0 bg-[#f5f4ef]/80 backdrop-blur-md z-30">
        <div className="flex items-center gap-3">
          <span className="rounded-full border border-[#20221f]/15 bg-white px-3.5 py-1.5 text-xs font-bold uppercase tracking-[0.16em] text-[#20221f]">
            Learning Paths
          </span>
          <Link
            href="/catalogue"
            className="hidden sm:inline-flex rounded-full border border-[#20221f]/10 bg-white/60 px-3.5 py-1.5 text-xs font-semibold text-[#20221f]/70 hover:text-[#ef6c4d] transition-colors"
          >
            Browse catalogue <ArrowUpRight className="ml-1 inline" size={13} />
          </Link>
        </div>

        {/* TOP RIGHT ASCENDR ELEMENT GOING BACK TO HOME */}
        <Link
          href="/"
          className="group flex items-center gap-2.5 sm:gap-3"
          aria-label="ascendr. home"
          title="Go to home page"
        >
          <span className="grid size-9 place-items-center rounded-full bg-[#20221f] text-[#f5f4ef] transition-transform group-hover:rotate-12 shadow-xs">
            <Compass size={18} />
          </span>
          <span className="font-bold tracking-[-0.04em] text-lg sm:text-xl text-[#20221f]">
            ascendr<span className="text-[#ef6c4d]">.</span>
          </span>
        </Link>
      </header>

      {/* HERO SECTION */}
      <section className="mx-auto max-w-7xl px-5 pb-20 pt-14 lg:px-10 lg:pb-28 lg:pt-20">
        <p className="mb-5 text-xs font-bold uppercase tracking-[0.2em] text-[#ef6c4d]">
          Learning paths / Choose your next move
        </p>
        <div className="grid gap-10 lg:grid-cols-[1.1fr_.9fr] lg:items-end">
          <h1 className="max-w-4xl text-6xl font-black leading-[.86] tracking-[-0.09em] lg:text-9xl">
            What should I learn, <span className="text-[#ef6c4d]">and in what order?</span>
          </h1>
          <p className="max-w-md text-lg leading-relaxed text-[#20221f]/65">
            Curated sequences for people who want direction without giving up the freedom to explore. Start where you are, then follow the thread.
          </p>
        </div>
      </section>

      {/* PATHS GRID */}
      <section className="border-y border-[#20221f]/10 px-5 py-16 lg:px-10 lg:py-20">
        <div className="mx-auto max-w-7xl">
          <div className="mb-10 flex flex-wrap gap-2 text-sm font-semibold">
            <a href="#fundamentals" className="rounded-full bg-[#f5cb54] px-4 py-2 hover:opacity-90 transition-opacity">Start from zero</a>
            <a href="#projects" className="rounded-full bg-[#bde8d4] px-4 py-2 hover:opacity-90 transition-opacity">Build a project</a>
            <a href="#career" className="rounded-full bg-[#e9d8ff] px-4 py-2 hover:opacity-90 transition-opacity">Prepare for work</a>
            <a href="#cloud" className="rounded-full border border-[#20221f]/15 bg-white px-4 py-2 hover:bg-[#20221f] hover:text-white transition-colors">Explore</a>
          </div>

          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {paths.map((path) => {
              const Icon = path.icon
              return (
                <Link
                  id={path.id}
                  href={`/paths/${path.slug}`}
                  key={path.slug}
                  className={`group flex min-h-[365px] flex-col justify-between rounded-3xl p-7 transition-transform hover:-translate-y-2 ${path.tone}`}
                >
                  <div className="flex items-start justify-between">
                    <Icon size={26} strokeWidth={1.5} />
                    <span className="text-xs font-bold uppercase tracking-[0.15em]">{path.number}</span>
                  </div>

                  <div className="mt-auto">
                    <p className="text-xs font-bold uppercase tracking-[0.14em] opacity-60">{path.label}</p>
                    <h2 className="mt-3 text-3xl font-black leading-none tracking-[-0.06em]">{path.title}</h2>
                    <p className="mt-4 max-w-sm text-sm leading-relaxed opacity-70">{path.description}</p>
                    <div className="mt-7 flex items-center justify-between border-t border-current/15 pt-4 text-xs font-semibold">
                      <span>{path.stages}</span>
                      <span>{path.outcome}</span>
                      <ArrowUpRight className="transition-transform group-hover:translate-x-1 group-hover:-translate-y-1" size={17} />
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      {/* CATALOGUE BANNER */}
      <section className="bg-[#ef6c4d] px-5 py-16 lg:px-10">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-6 md:flex-row md:items-end">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-white/65">Prefer to browse?</p>
            <h2 className="mt-3 max-w-xl text-4xl font-black leading-none tracking-[-0.06em] text-white lg:text-6xl">
              Start with the full library.
            </h2>
          </div>
          <Link
            href="/catalogue"
            className="rounded-full bg-[#20221f] px-6 py-4 font-bold text-white hover:bg-black transition-colors"
          >
            Open catalogue <ArrowUpRight className="ml-2 inline" size={17} />
          </Link>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="mx-auto max-w-7xl px-5 py-9 text-sm text-[#20221f]/50 lg:px-10 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="font-bold text-[#20221f]">
          ascendr<span className="text-[#ef6c4d]">.</span> — Curated Learning Sequences
        </div>
        <Link href="/" className="hover:text-[#ef6c4d] font-semibold transition-colors">
          Back to home
        </Link>
      </footer>
    </main>
  )
}
