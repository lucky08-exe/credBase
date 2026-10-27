'use client'

import React, { Suspense, useState, useEffect, useCallback, useRef } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import {
  ArrowLeft,
  ArrowUpRight,
  Clock,
  ExternalLink,
  Filter,
  Layers,
  RotateCcw,
  Search,
  SlidersHorizontal,
  Sparkles,
  X,
  Copy,
  Check,
  BookOpen,
  FlaskConical,
  Compass
} from 'lucide-react'

interface Credential {
  id: string
  title: string
  description: string
  duration: string | null
  duration_minutes: number | null
  url: string
  type: string
  level: string | null
  paid: boolean
}

interface FilterCounts {
  total: number
  types: Record<string, number>
  levels: Record<string, number>
  duration_brackets: Record<string, number>
}

const TRENDING_KEYWORDS = [
  'BigQuery',
  'Kubernetes',
  'Generative AI',
  'Terraform',
  'Security',
  'Vertex AI',
]

function CatalogueContent() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  // State from URL
  const queryParam = searchParams.get('q') || ''
  const typeParam = searchParams.get('type') || 'all'
  const levelParam = searchParams.get('level') || 'all'
  const durationParam = searchParams.get('duration_bracket') || 'all'
  const sortParam = searchParams.get('sort') || 'relevance'
  const pageParam = parseInt(searchParams.get('page') || '1', 10)

  // Local state
  const [searchInput, setSearchInput] = useState(queryParam)
  const [activeQuery, setActiveQuery] = useState(queryParam)
  const [selectedType, setSelectedType] = useState(typeParam)
  const [selectedLevel, setSelectedLevel] = useState(levelParam)
  const [selectedDuration, setSelectedDuration] = useState(durationParam)
  const [selectedSort, setSelectedSort] = useState(sortParam)
  const [currentPage, setCurrentPage] = useState(pageParam || 1)

  // Data & loading states
  const [credentials, setCredentials] = useState<Credential[]>([])
  const [totalCount, setTotalCount] = useState<number>(0)
  const [totalPages, setTotalPages] = useState<number>(1)
  const [loading, setLoading] = useState<boolean>(true)
  const [filterStats, setFilterStats] = useState<FilterCounts | null>(null)
  const [showMobileFilters, setShowMobileFilters] = useState<boolean>(false)

  // Modal detail state
  const [selectedCredential, setSelectedCredential] = useState<Credential | null>(null)
  const [copiedId, setCopiedId] = useState<boolean>(false)

  // Sync state when URL search params change
  useEffect(() => {
    const q = searchParams.get('q') || ''
    const t = searchParams.get('type') || 'all'
    const l = searchParams.get('level') || 'all'
    const d = searchParams.get('duration_bracket') || 'all'
    const s = searchParams.get('sort') || 'relevance'
    const p = parseInt(searchParams.get('page') || '1', 10)

    setSearchInput(q)
    setActiveQuery(q)
    setSelectedType(t)
    setSelectedLevel(l)
    setSelectedDuration(d)
    setSelectedSort(s)
    setCurrentPage(p || 1)
  }, [searchParams])

  // Update URL helper
  const updateURL = useCallback(
    (updates: {
      q?: string
      type?: string
      level?: string
      duration_bracket?: string
      sort?: string
      page?: number
    }) => {
      const current = new URLSearchParams(searchParams.toString())

      const nextQuery = updates.q !== undefined ? updates.q : activeQuery
      const nextType = updates.type !== undefined ? updates.type : selectedType
      const nextLevel = updates.level !== undefined ? updates.level : selectedLevel
      const nextDuration = updates.duration_bracket !== undefined ? updates.duration_bracket : selectedDuration
      const nextSort = updates.sort !== undefined ? updates.sort : selectedSort
      const nextPage = updates.page !== undefined ? updates.page : 1

      if (nextQuery) current.set('q', nextQuery)
      else current.delete('q')

      if (nextType && nextType !== 'all') current.set('type', nextType)
      else current.delete('type')

      if (nextLevel && nextLevel !== 'all') current.set('level', nextLevel)
      else current.delete('level')

      if (nextDuration && nextDuration !== 'all') current.set('duration_bracket', nextDuration)
      else current.delete('duration_bracket')

      if (nextSort && nextSort !== 'relevance') current.set('sort', nextSort)
      else current.delete('sort')

      if (nextPage && nextPage > 1) current.set('page', nextPage.toString())
      else current.delete('page')

      const queryString = current.toString()
      router.push(`${pathname}${queryString ? `?${queryString}` : ''}`, { scroll: false })
    },
    [activeQuery, selectedType, selectedLevel, selectedDuration, selectedSort, pathname, router, searchParams]
  )

  // Fetch filter facet stats once
  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch('/api/filters')
        if (res.ok) {
          const data = await res.json()
          setFilterStats(data)
        }
      } catch (err) {
        console.error('Error loading filters data:', err)
      }
    }
    fetchStats()
  }, [])

  // Debounced search handling
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const handleSearchChange = (val: string) => {
    setSearchInput(val)
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current)
    searchTimeoutRef.current = setTimeout(() => {
      setActiveQuery(val)
      setCurrentPage(1)
      updateURL({ q: val, page: 1 })
    }, 350)
  }

  const clearSearch = () => {
    setSearchInput('')
    setActiveQuery('')
    setCurrentPage(1)
    updateURL({ q: '', page: 1 })
  }

  // Fetch Credentials
  useEffect(() => {
    let isMounted = true
    async function loadData() {
      setLoading(true)
      const params = new URLSearchParams()
      if (activeQuery) params.set('q', activeQuery)
      if (selectedType && selectedType !== 'all') params.set('type', selectedType)
      if (selectedLevel && selectedLevel !== 'all') params.set('level', selectedLevel)
      if (selectedDuration && selectedDuration !== 'all') params.set('duration_bracket', selectedDuration)
      if (selectedSort) params.set('sort', selectedSort)
      params.set('page', currentPage.toString())
      params.set('page_size', '24')

      try {
        const res = await fetch(`/api/credentials?${params.toString()}`)
        if (res.ok && isMounted) {
          const data = await res.json()
          setCredentials(data.items || [])
          setTotalCount(data.total || 0)
          setTotalPages(data.total_pages || 1)
        }
      } catch (err) {
        console.error('Failed to fetch credentials:', err)
      } finally {
        if (isMounted) setLoading(false)
      }
    }

    loadData()
    return () => {
      isMounted = false
    }
  }, [activeQuery, selectedType, selectedLevel, selectedDuration, selectedSort, currentPage])

  // Filter setters
  const handleTypeSelect = (type: string) => {
    setSelectedType(type)
    setCurrentPage(1)
    updateURL({ type, page: 1 })
  }

  const handleLevelSelect = (level: string) => {
    setSelectedLevel(level)
    setCurrentPage(1)
    updateURL({ level, page: 1 })
  }

  const handleDurationSelect = (dur: string) => {
    setSelectedDuration(dur)
    setCurrentPage(1)
    updateURL({ duration_bracket: dur, page: 1 })
  }

  const handleSortSelect = (sort: string) => {
    setSelectedSort(sort)
    setCurrentPage(1)
    updateURL({ sort, page: 1 })
  }

  const resetAllFilters = () => {
    setSearchInput('')
    setActiveQuery('')
    setSelectedType('all')
    setSelectedLevel('all')
    setSelectedDuration('all')
    setSelectedSort('relevance')
    setCurrentPage(1)
    router.push(pathname, { scroll: false })
  }

  const copyCredentialLink = (cred: Credential) => {
    if (navigator?.clipboard) {
      navigator.clipboard.writeText(cred.url)
      setCopiedId(true)
      setTimeout(() => setCopiedId(false), 2000)
    }
  }

  const formatTypeLabel = (type: string) => {
    if (type === 'lab') return 'Hands-on Lab'
    if (type === 'course') return 'Skill Course'
    if (type === 'learning_path') return 'Learning Path'
    return type
  }

  const getTypeBadgeStyle = (type: string) => {
    if (type === 'lab') return 'bg-[#bde8d4] text-[#20221f]'
    if (type === 'course') return 'bg-[#e9d8ff] text-[#20221f]'
    if (type === 'learning_path') return 'bg-[#f5cb54] text-[#20221f]'
    return 'bg-[#20221f]/10 text-[#20221f]'
  }

  const getLevelDot = (level: string | null) => {
    const l = (level || '').toLowerCase()
    if (l === 'introductory') return 'bg-[#34a853]'
    if (l === 'intermediate') return 'bg-[#fbbc04]'
    if (l === 'advanced') return 'bg-[#ea4335]'
    return 'bg-slate-300'
  }

  const formatDurationDisplay = (mins: number | null, fallback: string | null) => {
    if (fallback) return fallback
    if (!mins) return 'Self-paced'
    if (mins < 60) return `${mins}m`
    const hrs = Math.floor(mins / 60)
    const rem = mins % 60
    return rem > 0 ? `${hrs}h ${rem}m` : `${hrs}h`
  }

  const hasActiveFilters =
    activeQuery !== '' ||
    selectedType !== 'all' ||
    selectedLevel !== 'all' ||
    selectedDuration !== 'all'

  return (
    <main className="min-h-screen bg-[#f5f4ef] text-[#20221f]">
      {/* HEADER */}
      <header className="border-b border-[#20221f]/10 bg-[#f5f4ef]/80 backdrop-blur-md sticky top-0 z-30">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-10">
          <div className="flex items-center gap-3">
            <span className="rounded-full border border-[#20221f]/15 bg-white px-3.5 py-1.5 text-xs font-bold uppercase tracking-[0.16em] text-[#20221f]">
              Catalogue
            </span>
            <Link
              href="/paths"
              className="hidden sm:inline-flex rounded-full border border-[#20221f]/10 bg-white/60 px-3.5 py-1.5 text-xs font-semibold text-[#20221f]/70 hover:text-[#ef6c4d] transition-colors"
            >
              Learning Paths <ArrowUpRight className="ml-1 inline" size={13} />
            </Link>
          </div>

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
        </div>
      </header>

      {/* HERO & SEARCH */}
      <section className="mx-auto max-w-7xl px-5 pt-10 pb-8 lg:px-10">
        <p className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-[#ef6c4d]">
          Explore credentials & labs
        </p>
        <h1 className="max-w-4xl text-5xl font-black leading-[.92] tracking-[-0.07em] sm:text-7xl lg:text-8xl">
          Find something <br />
          <span className="text-[#ef6c4d]">worth doing.</span>
        </h1>
        <p className="mt-6 max-w-2xl text-base sm:text-lg leading-relaxed text-[#20221f]/70">
          Search the catalog of official Google Cloud hands-on labs, skill courses, and credentials.
          Find the exact skills you want to build next.
        </p>

        {/* SEARCH BOX */}
        <div className="mt-8 grid gap-3 rounded-3xl bg-white p-2.5 shadow-sm border border-[#20221f]/10 md:grid-cols-[1fr_auto]">
          <label className="flex items-center gap-3 px-3">
            <Search className="text-[#ef6c4d] shrink-0" size={22} />
            <span className="sr-only">Search catalogue</span>
            <input
              type="text"
              value={searchInput}
              onChange={(e) => handleSearchChange(e.target.value)}
              placeholder="Search by skill, product (e.g. BigQuery, Kubernetes, GenAI)..."
              className="w-full bg-transparent py-3.5 text-base sm:text-lg outline-none placeholder:text-[#20221f]/40"
            />
            {searchInput && (
              <button
                onClick={clearSearch}
                className="p-1.5 text-[#20221f]/40 hover:text-[#20221f] transition-colors rounded-full"
                title="Clear search"
              >
                <X size={18} />
              </button>
            )}
          </label>
          <div className="flex items-center gap-2 px-2">
            <button
              onClick={() => setShowMobileFilters(!showMobileFilters)}
              className="lg:hidden flex items-center gap-2 rounded-2xl bg-[#20221f] px-5 py-3 text-sm font-bold text-white hover:bg-black transition-colors"
            >
              <SlidersHorizontal size={16} /> Filters
              {hasActiveFilters && <span className="size-2 rounded-full bg-[#ef6c4d]" />}
            </button>
          </div>
        </div>

        {/* TRENDING PILLS */}
        <div className="mt-4 flex flex-wrap items-center gap-2 text-xs">
          <span className="font-bold text-[#20221f]/50 uppercase tracking-wider mr-1">Trending:</span>
          {TRENDING_KEYWORDS.map((kw) => (
            <button
              key={kw}
              onClick={() => {
                setSearchInput(kw)
                setActiveQuery(kw)
                setCurrentPage(1)
                updateURL({ q: kw, page: 1 })
              }}
              className={`rounded-full px-3.5 py-1.5 font-medium transition-all ${
                activeQuery.toLowerCase() === kw.toLowerCase()
                  ? 'bg-[#20221f] text-white'
                  : 'bg-white border border-[#20221f]/10 hover:border-[#20221f]/30 text-[#20221f]/80'
              }`}
            >
              {kw}
            </button>
          ))}
          <button
            onClick={() => handleDurationSelect('<30m')}
            className={`rounded-full px-3.5 py-1.5 font-medium transition-all ${
              selectedDuration === '<30m'
                ? 'bg-[#20221f] text-white'
                : 'bg-white border border-[#20221f]/10 hover:border-[#20221f]/30 text-[#20221f]/80'
            }`}
          >
            ⚡ ≤ 30 min
          </button>
        </div>
      </section>

      {/* MAIN CATALOGUE LAYOUT */}
      <section className="mx-auto max-w-7xl px-5 pb-24 lg:px-10">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
          {/* SIDEBAR FILTERS (DESKTOP) */}
          <aside
            className={`lg:col-span-1 space-y-6 rounded-3xl bg-white p-6 border border-[#20221f]/10 shadow-sm ${
              showMobileFilters ? 'block' : 'hidden lg:block'
            } lg:sticky lg:top-24`}
          >
            <div className="flex items-center justify-between pb-3 border-b border-[#20221f]/10">
              <div className="flex items-center gap-2 font-black text-lg">
                <SlidersHorizontal size={18} className="text-[#ef6c4d]" /> Filters
              </div>
              {hasActiveFilters && (
                <button
                  onClick={resetAllFilters}
                  className="text-xs font-bold text-[#ef6c4d] hover:underline flex items-center gap-1"
                >
                  <RotateCcw size={12} /> Reset
                </button>
              )}
            </div>

            {/* Credential Type */}
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.14em] text-[#20221f]/60 mb-3">
                Credential Type
              </p>
              <div className="space-y-1.5">
                {[
                  { id: 'all', label: 'All Types', count: filterStats?.total },
                  { id: 'lab', label: 'Hands-on Lab', count: filterStats?.types?.lab },
                  { id: 'course', label: 'Skill Course', count: filterStats?.types?.course },
                  { id: 'learning_path', label: 'Learning Path', count: filterStats?.types?.learning_path },
                ].map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleTypeSelect(item.id)}
                    className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-2xl text-xs font-semibold transition-all ${
                      selectedType === item.id
                        ? 'bg-[#20221f] text-white shadow-xs'
                        : 'hover:bg-[#f5f4ef] text-[#20221f]/80'
                    }`}
                  >
                    <span>{item.label}</span>
                    {item.count !== undefined && (
                      <span
                        className={`text-[11px] px-2 py-0.5 rounded-full ${
                          selectedType === item.id ? 'bg-white/20 text-white' : 'bg-[#20221f]/5 text-[#20221f]/60'
                        }`}
                      >
                        {item.count}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Difficulty Level */}
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.14em] text-[#20221f]/60 mb-3">
                Difficulty Level
              </p>
              <div className="space-y-1.5">
                {[
                  { id: 'all', label: 'All Levels', count: filterStats?.total, dot: null },
                  { id: 'introductory', label: 'Introductory', count: filterStats?.levels?.introductory, dot: 'bg-[#34a853]' },
                  { id: 'intermediate', label: 'Intermediate', count: filterStats?.levels?.intermediate, dot: 'bg-[#fbbc04]' },
                  { id: 'advanced', label: 'Advanced', count: filterStats?.levels?.advanced, dot: 'bg-[#ea4335]' },
                  { id: 'unspecified', label: 'Unspecified', count: filterStats?.levels?.unspecified, dot: 'bg-slate-300' },
                ].map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleLevelSelect(item.id)}
                    className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-2xl text-xs font-semibold transition-all ${
                      selectedLevel === item.id
                        ? 'bg-[#20221f] text-white shadow-xs'
                        : 'hover:bg-[#f5f4ef] text-[#20221f]/80'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      {item.dot && <span className={`size-2 rounded-full ${item.dot}`} />}
                      {item.label}
                    </span>
                    {item.count !== undefined && (
                      <span
                        className={`text-[11px] px-2 py-0.5 rounded-full ${
                          selectedLevel === item.id ? 'bg-white/20 text-white' : 'bg-[#20221f]/5 text-[#20221f]/60'
                        }`}
                      >
                        {item.count}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Duration */}
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.14em] text-[#20221f]/60 mb-3">
                Duration
              </p>
              <div className="space-y-1.5">
                {[
                  { id: 'all', label: 'Any Duration', count: filterStats?.total },
                  { id: '<30m', label: '⚡ Quick (≤ 30 min)', count: filterStats?.duration_brackets?.['<30m'] },
                  { id: '<1h', label: '⏱️ Short (31 - 60 min)', count: filterStats?.duration_brackets?.['<1h'] },
                  { id: '1-3h', label: '📚 Medium (1 - 3 hours)', count: filterStats?.duration_brackets?.['1-3h'] },
                  { id: '>3h', label: '🎯 Deep Dive (> 3 hours)', count: filterStats?.duration_brackets?.['>3h'] },
                ].map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleDurationSelect(item.id)}
                    className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-2xl text-xs font-semibold transition-all ${
                      selectedDuration === item.id
                        ? 'bg-[#20221f] text-white shadow-xs'
                        : 'hover:bg-[#f5f4ef] text-[#20221f]/80'
                    }`}
                  >
                    <span>{item.label}</span>
                    {item.count !== undefined && (
                      <span
                        className={`text-[11px] px-2 py-0.5 rounded-full ${
                          selectedDuration === item.id ? 'bg-white/20 text-white' : 'bg-[#20221f]/5 text-[#20221f]/60'
                        }`}
                      >
                        {item.count}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </aside>

          {/* MAIN RESULTS COLUMN */}
          <div className="lg:col-span-3 space-y-6">
            {/* CONTROLS HEADER */}
            <div className="flex flex-wrap items-center justify-between gap-4 rounded-3xl bg-white p-5 border border-[#20221f]/10 shadow-sm">
              <div className="flex items-center gap-2">
                <span className="font-black text-sm text-[#20221f]">
                  {loading ? 'Searching credentials…' : `Showing ${totalCount.toLocaleString()} credentials`}
                </span>
                {loading && (
                  <span className="size-4 animate-spin rounded-full border-2 border-[#ef6c4d] border-t-transparent" />
                )}
              </div>

              <div className="flex items-center gap-3">
                <label htmlFor="sort-dropdown" className="text-xs font-bold text-[#20221f]/60 uppercase tracking-wider">
                  Sort:
                </label>
                <select
                  id="sort-dropdown"
                  value={selectedSort}
                  onChange={(e) => handleSortSelect(e.target.value)}
                  className="rounded-2xl border border-[#20221f]/15 bg-[#f5f4ef] px-4 py-2 text-xs font-bold text-[#20221f] outline-none cursor-pointer hover:bg-white transition-colors"
                >
                  <option value="relevance">Relevance / Best Match</option>
                  <option value="title_asc">Title (A – Z)</option>
                  <option value="title_desc">Title (Z – A)</option>
                  <option value="duration_asc">Shortest Duration</option>
                  <option value="duration_desc">Longest Duration</option>
                </select>
              </div>
            </div>

            {/* ACTIVE FILTERS PILLS */}
            {hasActiveFilters && (
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="font-bold text-[#20221f]/50">Active:</span>
                {activeQuery && (
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-white px-3 py-1 font-semibold border border-[#20221f]/15">
                    Query: &ldquo;{activeQuery}&rdquo;
                    <button onClick={clearSearch} className="hover:text-[#ef6c4d]">
                      <X size={14} />
                    </button>
                  </span>
                )}
                {selectedType !== 'all' && (
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-white px-3 py-1 font-semibold border border-[#20221f]/15">
                    Type: {formatTypeLabel(selectedType)}
                    <button onClick={() => handleTypeSelect('all')} className="hover:text-[#ef6c4d]">
                      <X size={14} />
                    </button>
                  </span>
                )}
                {selectedLevel !== 'all' && (
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-white px-3 py-1 font-semibold border border-[#20221f]/15 capitalize">
                    Level: {selectedLevel}
                    <button onClick={() => handleLevelSelect('all')} className="hover:text-[#ef6c4d]">
                      <X size={14} />
                    </button>
                  </span>
                )}
                {selectedDuration !== 'all' && (
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-white px-3 py-1 font-semibold border border-[#20221f]/15">
                    Duration: {selectedDuration}
                    <button onClick={() => handleDurationSelect('all')} className="hover:text-[#ef6c4d]">
                      <X size={14} />
                    </button>
                  </span>
                )}
                <button
                  onClick={resetAllFilters}
                  className="font-bold text-[#ef6c4d] hover:underline ml-1"
                >
                  Clear all
                </button>
              </div>
            )}

            {/* CARDS GRID */}
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div
                    key={i}
                    className="h-72 rounded-3xl bg-white/70 animate-pulse border border-[#20221f]/10 p-6 flex flex-col justify-between"
                  >
                    <div className="space-y-3">
                      <div className="h-6 w-24 bg-slate-200 rounded-full" />
                      <div className="h-6 w-3/4 bg-slate-200 rounded-lg mt-4" />
                      <div className="h-4 w-full bg-slate-200 rounded-lg mt-2" />
                      <div className="h-4 w-5/6 bg-slate-200 rounded-lg" />
                    </div>
                    <div className="h-10 w-full bg-slate-200 rounded-2xl" />
                  </div>
                ))}
              </div>
            ) : credentials.length === 0 ? (
              <div className="rounded-3xl bg-white p-12 text-center border border-[#20221f]/10">
                <div className="mx-auto grid size-16 place-items-center rounded-full bg-[#f5f4ef] text-[#20221f]/40 mb-4">
                  <Search size={28} />
                </div>
                <h3 className="text-2xl font-black tracking-tight text-[#20221f]">No credentials found</h3>
                <p className="mt-2 text-sm text-[#20221f]/60 max-w-md mx-auto">
                  We couldn&apos;t find anything matching your exact search and filter criteria. Try adjusting your query or resetting filters.
                </p>
                <button
                  onClick={resetAllFilters}
                  className="mt-6 rounded-full bg-[#ef6c4d] px-6 py-3 text-sm font-bold text-white hover:bg-[#d85839] transition-colors"
                >
                  Reset all filters
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                {credentials.map((cred) => {
                  return (
                    <article
                      key={cred.id}
                      className="group flex flex-col justify-between rounded-3xl bg-white p-6 border border-[#20221f]/10 shadow-xs hover:border-[#20221f]/30 hover:shadow-md transition-all"
                    >
                      <div>
                        {/* BADGES ROW */}
                        <div className="flex flex-wrap items-center gap-2 mb-4">
                          <span
                            className={`rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-wider ${getTypeBadgeStyle(
                              cred.type
                            )}`}
                          >
                            {formatTypeLabel(cred.type)}
                          </span>

                          <span className="flex items-center gap-1.5 rounded-full border border-[#20221f]/10 bg-[#f5f4ef] px-2.5 py-0.5 text-[11px] font-medium capitalize text-[#20221f]/80">
                            <span className={`size-2 rounded-full ${getLevelDot(cred.level)}`} />
                            {cred.level || 'Unspecified'}
                          </span>

                          <span className="ml-auto flex items-center gap-1 text-[11px] font-semibold text-[#20221f]/60">
                            <Clock size={12} />
                            {formatDurationDisplay(cred.duration_minutes, cred.duration)}
                          </span>
                        </div>

                        {/* TITLE */}
                        <h2
                          onClick={() => setSelectedCredential(cred)}
                          className="text-lg font-bold tracking-tight text-[#20221f] group-hover:text-[#ef6c4d] transition-colors cursor-pointer line-clamp-2"
                        >
                          {cred.title}
                        </h2>

                        {/* DESCRIPTION */}
                        <p className="mt-2 text-xs leading-relaxed text-[#20221f]/65 line-clamp-3">
                          {cred.description || 'No description available for this credential.'}
                        </p>
                      </div>

                      {/* ACTIONS FOOTER */}
                      <div className="mt-6 pt-4 border-t border-[#20221f]/10 flex items-center justify-between gap-2">
                        <button
                          onClick={() => setSelectedCredential(cred)}
                          className="rounded-full px-4 py-2 text-xs font-bold text-[#20221f] hover:bg-[#f5f4ef] transition-colors"
                        >
                          Quick View
                        </button>

                        <a
                          href={cred.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1.5 rounded-full bg-[#20221f] px-4 py-2 text-xs font-bold text-white hover:bg-black transition-transform hover:-translate-y-0.5"
                        >
                          Launch <ArrowUpRight size={14} />
                        </a>
                      </div>
                    </article>
                  )
                })}
              </div>
            )}

            {/* PAGINATION */}
            {totalPages > 1 && (
              <div className="flex flex-wrap items-center justify-between gap-4 rounded-3xl bg-white p-5 border border-[#20221f]/10 shadow-sm mt-8">
                <span className="text-xs font-bold text-[#20221f]/60">
                  Page {currentPage} of {totalPages}
                </span>

                <div className="flex items-center gap-2">
                  <button
                    disabled={currentPage <= 1}
                    onClick={() => {
                      const next = currentPage - 1
                      setCurrentPage(next)
                      updateURL({ page: next })
                    }}
                    className="rounded-full border border-[#20221f]/15 px-4 py-2 text-xs font-bold disabled:opacity-30 disabled:pointer-events-none hover:bg-[#f5f4ef] transition-colors"
                  >
                    Previous
                  </button>

                  {/* Quick page numbers around current page */}
                  <div className="hidden sm:flex items-center gap-1">
                    {Array.from({ length: Math.min(5, totalPages) }, (_, idx) => {
                      let p = idx + 1
                      if (totalPages > 5) {
                        if (currentPage > 3 && currentPage < totalPages - 2) {
                          p = currentPage - 2 + idx
                        } else if (currentPage >= totalPages - 2) {
                          p = totalPages - 4 + idx
                        }
                      }
                      return (
                        <button
                          key={p}
                          onClick={() => {
                            setCurrentPage(p)
                            updateURL({ page: p })
                          }}
                          className={`size-8 rounded-full text-xs font-bold transition-all ${
                            currentPage === p
                              ? 'bg-[#20221f] text-white'
                              : 'hover:bg-[#f5f4ef] text-[#20221f]/80'
                          }`}
                        >
                          {p}
                        </button>
                      )
                    })}
                  </div>

                  <button
                    disabled={currentPage >= totalPages}
                    onClick={() => {
                      const next = currentPage + 1
                      setCurrentPage(next)
                      updateURL({ page: next })
                    }}
                    className="rounded-full bg-[#20221f] px-4 py-2 text-xs font-bold text-white disabled:opacity-30 disabled:pointer-events-none hover:bg-black transition-colors"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* QUICK VIEW MODAL */}
      {selectedCredential && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-150">
          <div
            className="relative w-full max-w-2xl rounded-3xl bg-white p-7 sm:p-9 shadow-2xl border border-[#20221f]/10 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={() => setSelectedCredential(null)}
              className="absolute top-6 right-6 grid size-9 place-items-center rounded-full bg-[#f5f4ef] text-[#20221f] hover:bg-[#20221f] hover:text-white transition-colors"
              title="Close modal"
            >
              <X size={18} />
            </button>

            {/* Badges */}
            <div className="flex flex-wrap items-center gap-2 mb-4">
              <span
                className={`rounded-full px-3.5 py-1 text-xs font-bold uppercase tracking-wider ${getTypeBadgeStyle(
                  selectedCredential.type
                )}`}
              >
                {formatTypeLabel(selectedCredential.type)}
              </span>

              <span className="flex items-center gap-1.5 rounded-full border border-[#20221f]/10 bg-[#f5f4ef] px-3 py-1 text-xs font-semibold capitalize text-[#20221f]/80">
                <span className={`size-2 rounded-full ${getLevelDot(selectedCredential.level)}`} />
                {selectedCredential.level || 'Unspecified Level'}
              </span>

              <span className="flex items-center gap-1.5 rounded-full border border-[#20221f]/10 bg-[#f5f4ef] px-3 py-1 text-xs font-semibold text-[#20221f]/80">
                <Clock size={13} />
                {formatDurationDisplay(selectedCredential.duration_minutes, selectedCredential.duration)}
              </span>
            </div>

            {/* Title */}
            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-[#20221f]">
              {selectedCredential.title}
            </h2>

            {/* Description */}
            <div className="mt-6 text-sm sm:text-base leading-relaxed text-[#20221f]/75 whitespace-pre-line bg-[#f5f4ef]/60 p-5 rounded-2xl border border-[#20221f]/10">
              {selectedCredential.description || 'No detailed description provided for this credential.'}
            </div>

            {/* Actions */}
            <div className="mt-8 flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-[#20221f]/10">
              <button
                onClick={() => copyCredentialLink(selectedCredential)}
                className="flex items-center gap-2 rounded-full border border-[#20221f]/15 px-4 py-2.5 text-xs font-bold hover:bg-[#f5f4ef] transition-colors"
              >
                {copiedId ? <Check size={14} className="text-emerald-600" /> : <Copy size={14} />}
                {copiedId ? 'Link Copied!' : 'Copy Link'}
              </button>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setSelectedCredential(null)}
                  className="rounded-full px-5 py-2.5 text-xs font-bold text-[#20221f]/70 hover:text-[#20221f]"
                >
                  Close
                </button>

                <a
                  href={selectedCredential.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 rounded-full bg-[#ef6c4d] px-6 py-2.5 text-xs font-bold text-white hover:bg-[#d85839] transition-transform hover:-translate-y-0.5 shadow-sm"
                >
                  Launch on Google Cloud <ArrowUpRight size={15} />
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* FOOTER */}
      <footer className="mx-auto max-w-7xl px-5 py-9 text-sm text-[#20221f]/50 lg:px-10 border-t border-[#20221f]/10 mt-12 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="font-bold text-[#20221f]">ascendr<span className="text-[#ef6c4d]">.</span> — Free Catalog Explorer</div>
        <div className="flex items-center gap-5">
          <Link href="/paths" className="hover:text-[#ef6c4d] font-semibold transition-colors">
            Learning paths
          </Link>
          <Link href="/" className="hover:text-[#ef6c4d] font-semibold transition-colors">
            Back to home
          </Link>
        </div>
      </footer>
    </main>
  )
}

export default function CataloguePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#f5f4ef] flex items-center justify-center p-8">
          <div className="flex items-center gap-3 text-lg font-bold text-[#20221f]">
            <span className="size-5 animate-spin rounded-full border-2 border-[#ef6c4d] border-t-transparent" />
            Loading catalogue…
          </div>
        </div>
      }
    >
      <CatalogueContent />
    </Suspense>
  )
}
