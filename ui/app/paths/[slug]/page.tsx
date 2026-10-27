import Link from 'next/link'
import { ArrowLeft, ArrowUpRight, CheckCircle2, Clock3, Compass, ExternalLink } from 'lucide-react'

const pathData = {
  'backend-foundations': {
    label: 'For future builders',
    title: 'Backend development foundations',
    intro: 'Learn how applications move data, serve requests, and stay reliable behind the interface.',
    outcome: 'You will understand the core pieces of a backend and have a sequence for building with them.',
    stages: [
      {
        title: 'Understand requests',
        copy: 'Learn how browsers and services communicate through HTTP, routes, and responses.',
        resources: [{ name: 'HTTP and networking basics', source: 'web.dev', href: 'https://web.dev/learn/' }]
      },
      {
        title: 'Work with data',
        copy: 'Explore the role of databases, APIs, and validation in a useful application.',
        resources: [{ name: 'Cloud SQL and databases', source: 'Google Cloud', href: 'https://cloud.google.com/learn/what-is-a-database' }]
      },
      {
        title: 'Ship a service',
        copy: 'Connect the pieces and learn what makes a backend dependable in practice.',
        resources: [{ name: 'Google Cloud architecture center', source: 'Google Cloud', href: 'https://cloud.google.com/architecture' }]
      }
    ]
  },
  'cloud-computing': {
    label: 'For systems thinkers',
    title: 'Cloud computing fundamentals',
    intro: 'Understand the building blocks behind modern apps: compute, storage, networks, and deployment.',
    outcome: 'You will be able to describe how a cloud application is assembled and what to learn next.',
    stages: [
      {
        title: 'Map the building blocks',
        copy: 'Get familiar with compute, storage, networking, and managed services.',
        resources: [{ name: 'What is cloud computing?', source: 'Google Cloud', href: 'https://cloud.google.com/learn/what-is-cloud-computing' }]
      },
      {
        title: 'Explore deployment',
        copy: 'See how teams package, deploy, and observe software in the cloud.',
        resources: [{ name: 'Google Cloud Skills Boost', source: 'Google Cloud', href: 'https://www.cloudskillsboost.google/paths/11' }]
      },
      {
        title: 'Think in systems',
        copy: 'Practice choosing services based on reliability, scale, and the people using them.',
        resources: [{ name: 'Cloud architecture framework', source: 'Google Cloud', href: 'https://cloud.google.com/architecture/framework' }]
      }
    ]
  },
  'first-steps-ai-ml': {
    label: 'For curious beginners',
    title: 'First steps into AI / ML',
    intro: 'Build a plain-language mental model of machine learning, then try the ideas hands-on.',
    outcome: 'You will be able to explain the core ideas behind modern AI and choose a sensible next step.',
    stages: [
      {
        title: 'Get oriented',
        copy: 'Learn the vocabulary: data, models, training, inference, and evaluation.',
        resources: [{ name: 'Machine Learning Crash Course', source: 'Google for Developers', href: 'https://developers.google.com/machine-learning/crash-course' }]
      },
      {
        title: 'Understand the workflow',
        copy: 'See how a problem becomes a dataset, a model, and a measurable result.',
        resources: [{ name: 'Introduction to Machine Learning', source: 'Google Cloud Skills Boost', href: 'https://www.cloudskillsboost.google/paths/17' }]
      },
      {
        title: 'Try it yourself',
        copy: 'Use a guided notebook to move from concept to a small experiment.',
        resources: [{ name: 'Colab notebooks', source: 'Google Colab', href: 'https://colab.research.google.com/' }]
      }
    ]
  },
  'first-practical-project': {
    label: 'For learning by doing',
    title: 'Build a first practical project',
    intro: 'Go from a small idea to a finished project with a scope you can actually complete.',
    outcome: 'You will have a small, explainable project and a repeatable way to keep building.',
    stages: [
      {
        title: 'Choose a useful question',
        copy: 'Define a user, a problem, and one outcome before choosing tools.',
        resources: [{ name: 'Build with Google AI', source: 'Google for Developers', href: 'https://ai.google.dev/' }]
      },
      {
        title: 'Make the smallest version',
        copy: 'Learn the loop of prototyping, testing, and making one improvement at a time.',
        resources: [{ name: 'Web development basics', source: 'web.dev', href: 'https://web.dev/learn/' }]
      },
      {
        title: 'Share what you learned',
        copy: 'Document the decisions, tradeoffs, and next iteration.',
        resources: [{ name: 'Technical writing for developers', source: 'Google Technical Writing', href: 'https://developers.google.com/tech-writing' }]
      }
    ]
  },
  'technical-internship-prep': {
    label: 'For early-career learners',
    title: 'Prepare for technical internships',
    intro: 'Turn your foundations into evidence: projects, technical fluency, and a story about how you learn.',
    outcome: 'You will be ready to talk clearly about your work and identify the gaps worth closing next.',
    stages: [
      {
        title: 'Strengthen your foundations',
        copy: 'Review core concepts and practice explaining them without jargon.',
        resources: [{ name: 'Google IT Automation with Python', source: 'Google Career Certificates', href: 'https://grow.google/certificates/it-support/' }]
      },
      {
        title: 'Build evidence',
        copy: 'Choose one project that shows how you think, not just what tools you used.',
        resources: [{ name: 'Project-based learning resources', source: 'Google for Developers', href: 'https://developers.google.com/learn' }]
      },
      {
        title: 'Practice the conversation',
        copy: 'Prepare a concise story about your choices, your mistakes, and what you would improve.',
        resources: [{ name: 'Technical interviewing resources', source: 'Google Careers', href: 'https://careers.google.com/how-we-hire/interview/' }]
      }
    ]
  },
}

export function generateStaticParams() {
  return Object.keys(pathData).map((slug) => ({ slug }))
}

export default async function PathDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const path = pathData[slug as keyof typeof pathData]

  if (!path) {
    return (
      <main className="min-h-screen bg-[#f5f4ef] p-10 text-[#20221f]">
        <Link href="/paths" className="font-bold text-[#ef6c4d] hover:underline">
          <ArrowLeft className="mr-1 inline" size={16} /> Back to paths
        </Link>
        <h1 className="mt-20 text-6xl font-black">Path not found.</h1>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-[#f5f4ef] text-[#20221f]">
      {/* HEADER */}
      <header className="mx-auto flex max-w-5xl items-center justify-between px-5 py-6 lg:px-10 border-b border-[#20221f]/10 sticky top-0 bg-[#f5f4ef]/80 backdrop-blur-md z-30">
        <div className="flex items-center gap-3">
          <Link
            href="/paths"
            className="group inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-[#20221f]/70 hover:text-[#ef6c4d] transition-colors"
          >
            <ArrowLeft className="text-[#ef6c4d] transition-transform group-hover:-translate-x-0.5" size={15} /> All paths
          </Link>
          <span className="h-4 w-px bg-[#20221f]/15" />
          <Link
            href="/catalogue"
            className="text-xs font-semibold text-[#20221f]/70 hover:text-[#ef6c4d] transition-colors"
          >
            Catalogue <ArrowUpRight className="ml-0.5 inline" size={12} />
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
      <section className="mx-auto max-w-5xl px-5 pb-20 pt-16 lg:px-10 lg:pt-24">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#ef6c4d]">{path.label}</p>
        <h1 className="mt-5 max-w-4xl text-6xl font-black leading-[.86] tracking-[-0.08em] lg:text-9xl">
          {path.title}
        </h1>
        <p className="mt-8 max-w-2xl text-xl leading-relaxed text-[#20221f]/65">{path.intro}</p>
        <div className="mt-10 flex flex-wrap gap-6 text-sm font-semibold">
          <span>
            <CheckCircle2 className="mr-2 inline text-[#ef6c4d]" size={18} /> Curated sequence
          </span>
          <span>
            <Clock3 className="mr-2 inline text-[#ef6c4d]" size={18} /> Move at your pace
          </span>
        </div>
      </section>

      {/* STAGES & PRACTICAL OUTCOME */}
      <section className="border-y border-[#20221f]/10 bg-white px-5 py-16 lg:px-10 lg:py-24">
        <div className="mx-auto max-w-5xl">
          <div className="mb-12 rounded-3xl bg-[#bde8d4] p-7 lg:p-10">
            <p className="text-xs font-bold uppercase tracking-[0.2em]">The practical outcome</p>
            <p className="mt-4 max-w-2xl text-2xl font-bold leading-tight tracking-[-0.04em]">
              {path.outcome}
            </p>
          </div>

          <div className="flex flex-col gap-8">
            {path.stages.map((stage, index) => (
              <article key={stage.title} className="grid gap-6 border-t border-[#20221f]/15 pt-7 lg:grid-cols-[90px_1fr_1fr]">
                <span className="text-5xl font-black tracking-[-0.08em] text-[#ef6c4d]">0{index + 1}</span>
                <div>
                  <h2 className="text-3xl font-black tracking-[-0.05em]">{stage.title}</h2>
                  <p className="mt-3 max-w-md leading-relaxed text-[#20221f]/60">{stage.copy}</p>
                </div>
                <div className="flex flex-col gap-3">
                  {stage.resources.map((resource) => (
                    <a
                      href={resource.href}
                      target="_blank"
                      rel="noreferrer"
                      key={resource.name}
                      className="group rounded-2xl border border-[#20221f]/15 p-4 transition-colors hover:bg-[#f5cb54]"
                    >
                      <p className="font-bold">
                        {resource.name} <ExternalLink className="ml-1 inline opacity-50" size={14} />
                      </p>
                      <p className="mt-1 text-xs uppercase tracking-[0.12em] opacity-50">{resource.source}</p>
                    </a>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="mx-auto flex max-w-5xl justify-between px-5 py-9 text-sm text-[#20221f]/60 lg:px-10">
        <Link href="/paths" className="hover:text-[#ef6c4d] font-semibold transition-colors">
          <ArrowLeft className="mr-1 inline" size={14} /> Choose another path
        </Link>
        <Link href="/catalogue" className="hover:text-[#ef6c4d] font-semibold transition-colors">
          See full catalogue <ArrowUpRight className="ml-1 inline" size={14} />
        </Link>
      </footer>
    </main>
  )
}
