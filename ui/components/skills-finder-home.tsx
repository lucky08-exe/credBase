'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { ArrowUpRight, Brain, Check, Cloud, Compass, Menu, Sparkles, Target, X } from 'lucide-react'
import { useState } from 'react'

const goals = [
  { title: 'Break into AI / ML', copy: 'Build the mental model before the model.', icon: Brain, tone: 'sun' },
  { title: 'Get internship-ready', copy: 'Turn “I’m learning” into work you can show.', icon: Target, tone: 'ink' },
  { title: 'Make a real project', copy: 'Find a path that ends in something useful.', icon: Sparkles, tone: 'mint' },
  { title: 'Explore cloud', copy: 'See how the pieces connect in the real world.', icon: Cloud, tone: 'lavender' },
]

const paths = [
  { eyebrow: 'A clear first step', title: 'Start with the fundamentals', description: 'A gentle way into technical learning when every tab feels like a different opinion.', level: 'New to tech', outcome: 'A map of what to learn next', tone: 'sun', id: 'fundamentals' },
  { eyebrow: 'Build while learning', title: 'From idea to working project', description: 'Pick a direction, follow the thread, and finish with something you can explain.', level: 'Some experience', outcome: 'A project to put on your portfolio', tone: 'mint', id: 'projects' },
  { eyebrow: 'Credentials that count', title: 'Make your progress visible', description: 'Explore learning experiences that can lead to credentials you can share.', level: 'Ready to go deeper', outcome: 'A signal of what you know', tone: 'lavender', id: 'career' },
]

export function AscendrHome() {
  const router = useRouter()
  const [menuOpen, setMenuOpen] = useState(false)
  const [prompt, setPrompt] = useState('')

  function submitPrompt(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!prompt.trim()) return
    router.push(`/catalogue?q=${encodeURIComponent(prompt.trim())}`)
  }

  return (
    <main className="min-h-screen overflow-hidden bg-[#f5f4ef] text-[#20221f]">
      {/* NAVIGATION */}
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-5 py-6 lg:px-10" aria-label="Main navigation">
        <Link href="/" className="group flex items-center gap-3" aria-label="ascendr. home">
          <span className="grid size-9 place-items-center rounded-full bg-[#20221f] text-[#f5f4ef] transition-transform group-hover:rotate-12">
            <Compass size={18} />
          </span>
          <span className="font-bold tracking-[-0.04em] text-xl">
            ascendr<span className="text-[#ef6c4d]">.</span>
          </span>
        </Link>
        <div className="hidden items-center gap-8 text-sm font-medium lg:flex">
          <a href="#home" className="hover:text-[#ef6c4d] transition-colors">Home</a>
          <Link href="/paths" className="hover:text-[#ef6c4d] transition-colors">Learning paths</Link>
          <Link href="/catalogue" className="hover:text-[#ef6c4d] transition-colors">Explore credentials</Link>
          <a href="#guide" className="hover:text-[#ef6c4d] transition-colors">AI guide</a>
        </div>
        <Link
          href="/paths"
          className="hidden rounded-full bg-[#20221f] px-5 py-3 text-sm font-semibold text-[#f5f4ef] transition-transform hover:-translate-y-0.5 lg:block shadow-sm"
        >
          Find my path <ArrowUpRight className="ml-1 inline" size={15} />
        </Link>
        <button
          className="rounded-full border border-[#20221f]/15 p-2 lg:hidden"
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </nav>

      {menuOpen && (
        <div className="mx-5 flex flex-col gap-4 rounded-2xl border border-[#20221f]/10 bg-white p-5 lg:hidden shadow-lg">
          <a href="#home" onClick={() => setMenuOpen(false)} className="font-medium hover:text-[#ef6c4d]">Home</a>
          <Link href="/paths" onClick={() => setMenuOpen(false)} className="font-medium hover:text-[#ef6c4d]">Learning paths</Link>
          <Link href="/catalogue" onClick={() => setMenuOpen(false)} className="font-medium hover:text-[#ef6c4d]">Explore credentials</Link>
          <a href="#guide" onClick={() => setMenuOpen(false)} className="font-medium hover:text-[#ef6c4d]">AI guide</a>
        </div>
      )}

      {/* HERO SECTION */}
      <section id="home" className="mx-auto grid max-w-7xl gap-10 px-5 pb-20 pt-12 lg:grid-cols-[1.1fr_.9fr] lg:px-10 lg:pb-28 lg:pt-20">
        <div className="relative z-10">
          <p className="mb-7 flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-[#ef6c4d]">
            <span className="size-2 rounded-full bg-[#ef6c4d]" /> A learning guide for your next move
          </p>
          <h1 className="max-w-4xl text-[clamp(4rem,10vw,9.5rem)] font-black leading-[.82] tracking-[-0.09em]">
            Confused?<br />
            <span className="text-[#ef6c4d]">Even we</span> were.
          </h1>
          <p className="mt-9 max-w-lg text-lg leading-relaxed text-[#20221f]/65 lg:text-xl">
            Too many courses. Too many skills. No idea where to start. ascendr. helps you find a direction, discover hands-on learning, and make progress you can point to.
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <Link
              href="/paths"
              className="rounded-full bg-[#ef6c4d] px-6 py-4 font-bold text-white transition-transform hover:-translate-y-1 shadow-sm"
            >
              Help me find my path <ArrowUpRight className="ml-2 inline" size={17} />
            </Link>
            <Link
              href="/catalogue"
              className="rounded-full border border-[#20221f]/20 px-6 py-4 font-bold hover:bg-white transition-colors"
            >
              Explore credentials
            </Link>
          </div>
        </div>
        <div className="relative min-h-[400px] lg:min-h-[590px]">
          <div className="absolute right-0 top-6 h-64 w-64 rounded-[42%_58%_61%_39%/50%_41%_59%_50%] bg-[#e9d8ff] lg:h-96 lg:w-96" />
          <div className="absolute bottom-8 left-3 z-10 w-64 rotate-[-7deg] rounded-3xl bg-[#20221f] p-6 text-[#f5f4ef] shadow-2xl lg:left-10 lg:w-80">
            <p className="text-xs uppercase tracking-[0.18em] text-[#f5f4ef]/50">A gentle nudge</p>
            <p className="mt-5 text-3xl font-bold leading-tight tracking-[-0.05em]">You don&apos;t need a five-year plan. Just a better next step.</p>
            <div className="mt-8 flex items-center gap-2 text-sm text-[#f5f4ef]/60">
              <span className="grid size-8 place-items-center rounded-full bg-[#ef6c4d] text-white">
                <Check size={15} />
              </span>
              No gatekeeping
            </div>
          </div>
          <div className="absolute right-3 top-24 z-10 w-44 rotate-[9deg] rounded-3xl border border-[#20221f]/10 bg-white p-5 shadow-xl lg:right-12 lg:top-32">
            <div className="mb-12 flex justify-between text-xs font-bold">
              <span>01</span>
              <span>GO</span>
            </div>
            <p className="text-2xl font-black leading-none tracking-[-0.06em]">Start<br />curious.</p>
          </div>
          <div className="absolute bottom-12 right-0 rounded-full border border-[#20221f]/15 px-5 py-3 text-sm font-semibold lg:right-8 bg-white/70 backdrop-blur-xs">
            Less scrolling. More doing.
          </div>
        </div>
      </section>

      {/* GOALS SECTION */}
      <section className="mx-auto max-w-7xl px-5 pb-24 lg:px-10">
        <div className="grid gap-5 md:grid-cols-4">
          {goals.map((goal) => {
            const Icon = goal.icon
            return (
              <Link
                href="/paths"
                key={goal.title}
                className={`group min-h-52 rounded-3xl p-6 transition-transform hover:-translate-y-2 flex flex-col justify-between ${
                  goal.tone === 'sun'
                    ? 'bg-[#f5cb54] text-[#20221f]'
                    : goal.tone === 'ink'
                    ? 'bg-[#20221f] text-[#f5f4ef]'
                    : goal.tone === 'mint'
                    ? 'bg-[#bde8d4] text-[#20221f]'
                    : 'bg-[#e9d8ff] text-[#20221f]'
                }`}
              >
                <Icon size={25} strokeWidth={1.5} />
                <div>
                  <h2 className="text-xl font-bold tracking-[-0.04em]">{goal.title}</h2>
                  <p className="mt-2 text-sm opacity-75">{goal.copy}</p>
                </div>
                <ArrowUpRight className="ml-auto opacity-50 transition-transform group-hover:translate-x-1 group-hover:-translate-y-1" size={18} />
              </Link>
            )
          })}
        </div>
      </section>

      {/* AI GUIDE SECTION */}
      <section id="guide" className="border-y border-[#20221f]/10 bg-[#20221f] px-5 py-20 text-[#f5f4ef] lg:px-10 lg:py-28">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-12 lg:grid-cols-[.8fr_1.2fr] lg:items-end">
            <div>
              <p className="mb-5 text-xs font-bold uppercase tracking-[0.2em] text-[#f5cb54]">01 / Tell us anything</p>
              <h2 className="max-w-xl text-5xl font-black leading-[.9] tracking-[-0.07em] lg:text-7xl">Start with what&apos;s on your mind.</h2>
            </div>
            <div>
              <form onSubmit={submitPrompt} className="flex flex-col gap-4 border-b border-[#f5f4ef]/30 pb-4 sm:flex-row">
                <label htmlFor="learning-goal" className="sr-only">Describe your learning goal</label>
                <input
                  id="learning-goal"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="“I want to build something with AI…”"
                  className="min-w-0 flex-1 bg-transparent py-3 text-xl outline-none placeholder:text-[#f5f4ef]/35 text-[#f5f4ef]"
                />
                <button type="submit" className="rounded-full bg-[#f5cb54] px-6 py-3 font-bold text-[#20221f] hover:bg-[#ebd550] transition-colors cursor-pointer">
                  Go <ArrowUpRight className="ml-1 inline" size={16} />
                </button>
              </form>
              <p className="mt-4 text-sm text-[#f5f4ef]/50">No perfect wording required. Hit Go to search matching credentials, labs, and courses.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CURATED DIRECTIONS */}
      <section id="paths" className="mx-auto max-w-7xl px-5 py-24 lg:px-10 lg:py-32">
        <div className="mb-12 flex flex-col justify-between gap-5 md:flex-row md:items-end">
          <div>
            <p className="mb-4 text-xs font-bold uppercase tracking-[0.2em] text-[#ef6c4d]">02 / Curated directions</p>
            <h2 className="max-w-xl text-5xl font-black leading-[.9] tracking-[-0.07em] lg:text-7xl">A path beats a pile.</h2>
          </div>
          <p className="max-w-xs text-sm leading-relaxed text-[#20221f]/60">A few ways to move forward, depending on where you are now. No made-up promises — just useful starting points.</p>
        </div>
        <div className="grid gap-5 lg:grid-cols-3">
          {paths.map((path, index) => (
            <Link
              href={`/paths#${path.id}`}
              key={path.title}
              className={`group flex flex-col justify-between rounded-3xl p-7 transition-transform hover:-translate-y-2 ${
                path.tone === 'sun' ? 'bg-[#f5cb54]' : path.tone === 'mint' ? 'bg-[#bde8d4]' : 'bg-[#e9d8ff]'
              }`}
            >
              <div>
                <div className="flex justify-between text-xs font-bold uppercase tracking-[0.14em]">
                  <span>{path.eyebrow}</span>
                  <span>0{index + 1}</span>
                </div>
                <h3 className="mt-20 text-3xl font-black leading-tight tracking-[-0.06em] group-hover:text-[#ef6c4d] transition-colors">{path.title}</h3>
                <p className="mt-4 text-sm leading-relaxed opacity-75">{path.description}</p>
              </div>
              <div className="mt-8 border-t border-[#20221f]/15 pt-4 text-xs font-semibold flex items-center justify-between">
                <div>
                  <span>{path.level}</span>
                  <span className="mx-2 opacity-40">/</span>
                  <span>{path.outcome}</span>
                </div>
                <ArrowUpRight className="opacity-40 group-hover:opacity-100 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" size={16} />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* CATALOGUE BANNER */}
      <section className="bg-[#ef6c4d] px-5 py-20 lg:px-10 lg:py-24">
        <div className="mx-auto flex max-w-7xl flex-col items-start justify-between gap-8 md:flex-row md:items-end">
          <div>
            <p className="mb-4 text-xs font-bold uppercase tracking-[0.2em] text-white/70">03 / The full catalogue</p>
            <h2 className="max-w-2xl text-5xl font-black leading-[.9] tracking-[-0.07em] text-white lg:text-7xl">When you&apos;re ready to go browsing.</h2>
          </div>
          <Link href="/catalogue" className="rounded-full bg-[#20221f] px-6 py-4 font-bold text-[#f5f4ef] hover:bg-black transition-colors shadow-lg">
            Open the catalogue <ArrowUpRight className="ml-2 inline" size={17} />
          </Link>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-9 text-sm lg:flex-row lg:items-center lg:justify-between lg:px-10">
        <div className="font-bold">ascendr<span className="text-[#ef6c4d]">.</span></div>
        <div className="flex gap-5 text-[#20221f]/60">
          <a href="#home">Home</a>
          <Link href="/paths">Learning paths</Link>
          <Link href="/catalogue">Credentials</Link>
          <a href="#guide">AI guide</a>
        </div>
        <p className="text-[#20221f]/45">A student-friendly starting point.</p>
      </footer>
    </main>
  )
}

// Export both names for backwards compatibility
export { AscendrHome as SkillsFinderHome }
