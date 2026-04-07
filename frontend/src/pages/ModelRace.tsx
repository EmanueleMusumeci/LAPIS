/**
 * ModelRace - Benchmark comparison dashboard showing multiple methods/models side-by-side.
 */
import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { fetchModelRaceData } from '@/lib/api'
import type { ModelRaceData, BenchmarkSummary } from '@/types'
import { cn } from '@/lib/utils'
import { TrendingUp, Award, Zap, Clock, BookOpen, Wifi } from 'lucide-react'

// ── Paper results (from published paper, Claude Sonnet 4.6 + FastDownward) ────

type PaperRow = {
  domain: string
  llmpp_few: number | null
  llmpp_zero: number | null
  nl2plan: number | null
  gt_lapis: number | null
  lapis_zero: number | null
  lapis_dom: number | null
  lapis_adq: number | null
  sim_val: number
  sim_gt: number
}

const PAPER_ROWS: PaperRow[] = [
  { domain: 'Blocksworld', llmpp_few: 100, llmpp_zero: 80,  nl2plan: 95,   gt_lapis: 100, lapis_zero: 100, lapis_dom: 100, lapis_adq: 100, sim_val: 100, sim_gt: 90 },
  { domain: 'Floortile',   llmpp_few: 100, llmpp_zero: 45,  nl2plan: null, gt_lapis: 90,  lapis_zero: 90,  lapis_dom: 90,  lapis_adq: 85,  sim_val: 100, sim_gt: 75 },
  { domain: 'Tyreworld',   llmpp_few: 95,  llmpp_zero: 90,  nl2plan: null, gt_lapis: 95,  lapis_zero: 75,  lapis_dom: 75,  lapis_adq: 75,  sim_val: 100, sim_gt: 45 },
  { domain: 'Storage',     llmpp_few: 100, llmpp_zero: 90,  nl2plan: 25,   gt_lapis: 100, lapis_zero: 75,  lapis_dom: 100, lapis_adq: 100, sim_val: 100, sim_gt: 35 },
  { domain: 'Barman',      llmpp_few: 95,  llmpp_zero: 0,   nl2plan: null, gt_lapis: 80,  lapis_zero: 0,   lapis_dom: 50,  lapis_adq: 100, sim_val: 100, sim_gt: 90 },
  { domain: 'Grippers',    llmpp_few: 100, llmpp_zero: 100, nl2plan: null, gt_lapis: 100, lapis_zero: 100, lapis_dom: 100, lapis_adq: 100, sim_val: 100, sim_gt: 90 },
  { domain: 'Termes',      llmpp_few: 100, llmpp_zero: 95,  nl2plan: null, gt_lapis: 100, lapis_zero: 95,  lapis_dom: 100, lapis_adq: 100, sim_val: 100, sim_gt: 85 },
  { domain: 'Average',     llmpp_few: 99,  llmpp_zero: 71,  nl2plan: null, gt_lapis: 95,  lapis_zero: 76,  lapis_dom: 85,  lapis_adq: 96,  sim_val: 100, sim_gt: 73 },
]

function PaperResultsTable() {
  const fmt = (v: number | null) => v == null ? <span className="text-lapis-muted">—</span> : `${v}`
  const pct = (v: number) => {
    if (v >= 90) return 'text-emerald-400 font-semibold'
    if (v >= 70) return 'text-yellow-400 font-semibold'
    if (v >= 40) return 'text-orange-400'
    return 'text-rose-400'
  }

  return (
    <div className="bg-lapis-card border border-lapis-border rounded-xl overflow-hidden">
      <div className="px-6 py-4 border-b border-lapis-border">
        <h3 className="text-lg font-semibold text-lapis-text">Paper Benchmark Results</h3>
        <p className="text-xs text-lapis-muted mt-1">
          Claude Sonnet 4.6 + FastDownward · 20 problems/domain · A = VAL self-consistency % · B = GT simulator executability %
          <br />
          <span className="text-lapis-muted/70">* Uses ground-truth domains &nbsp;·&nbsp; Baselines achieve high VAL% but 0% GT executability</span>
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-lapis-bg/50 text-lapis-muted">
              <th className="px-4 py-3 text-left font-medium" rowSpan={2}>Domain</th>
              <th className="px-4 py-3 text-center font-medium border-l border-lapis-border" colSpan={2}>LLM+P *</th>
              <th className="px-4 py-3 text-center font-medium border-l border-lapis-border">NL2Plan</th>
              <th className="px-4 py-3 text-center font-medium border-l border-lapis-border">GT-LAPIS² *</th>
              <th className="px-4 py-3 text-center font-medium border-l border-lapis-border" colSpan={3}>LAPIS²</th>
              <th className="px-4 py-3 text-center font-medium border-l border-lapis-border bg-cyan-500/10 text-cyan-300">Sim-LAPIS²</th>
            </tr>
            <tr className="bg-lapis-bg/30 text-lapis-muted text-xs">
              <th className="px-3 py-2 text-center font-normal border-l border-lapis-border">Few-shot</th>
              <th className="px-3 py-2 text-center font-normal">Zero-shot</th>
              <th className="px-3 py-2 text-center font-normal border-l border-lapis-border">325s/task</th>
              <th className="px-3 py-2 text-center font-normal border-l border-lapis-border">GT domain</th>
              <th className="px-3 py-2 text-center font-normal border-l border-lapis-border">Zero</th>
              <th className="px-3 py-2 text-center font-normal">Dom.</th>
              <th className="px-3 py-2 text-center font-normal">Adq.</th>
              <th className="px-3 py-2 text-center font-normal border-l border-lapis-border bg-cyan-500/10 text-cyan-300">VAL / GT</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-lapis-border">
            {PAPER_ROWS.map((row) => (
              <tr key={row.domain} className={cn(
                'hover:bg-lapis-bg/30 transition-colors',
                row.domain === 'Average' && 'bg-lapis-bg/50 font-semibold'
              )}>
                <td className="px-4 py-3 text-lapis-text">{row.domain}</td>
                <td className="px-4 py-3 text-center border-l border-lapis-border">
                  {row.llmpp_few != null ? <span className={pct(row.llmpp_few)}>{fmt(row.llmpp_few)}</span> : fmt(null)}
                </td>
                <td className="px-4 py-3 text-center">
                  {row.llmpp_zero != null ? <span className={pct(row.llmpp_zero)}>{fmt(row.llmpp_zero)}</span> : fmt(null)}
                </td>
                <td className="px-4 py-3 text-center border-l border-lapis-border">
                  {row.nl2plan != null ? <span className={pct(row.nl2plan)}>{fmt(row.nl2plan)}</span> : fmt(null)}
                </td>
                <td className="px-4 py-3 text-center border-l border-lapis-border">
                  {row.gt_lapis != null ? <span className={pct(row.gt_lapis)}>{fmt(row.gt_lapis)}</span> : fmt(null)}
                </td>
                <td className="px-4 py-3 text-center border-l border-lapis-border">
                  {row.lapis_zero != null ? <span className={pct(row.lapis_zero)}>{fmt(row.lapis_zero)}</span> : fmt(null)}
                </td>
                <td className="px-4 py-3 text-center">
                  {row.lapis_dom != null ? <span className={pct(row.lapis_dom)}>{fmt(row.lapis_dom)}</span> : fmt(null)}
                </td>
                <td className="px-4 py-3 text-center">
                  {row.lapis_adq != null ? <span className={pct(row.lapis_adq)}>{fmt(row.lapis_adq)}</span> : fmt(null)}
                </td>
                <td className="px-4 py-3 text-center border-l border-lapis-border bg-cyan-500/5">
                  <span className={pct(row.sim_val)}>{row.sim_val}</span>
                  <span className="text-lapis-muted mx-1">/</span>
                  <span className={pct(row.sim_gt)}>{row.sim_gt}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-6 py-3 border-t border-lapis-border bg-lapis-bg/30">
        <p className="text-xs text-lapis-muted">
          <strong className="text-lapis-text">The validation gap:</strong> Baselines achieve high self-consistency but{' '}
          <strong className="text-rose-400">0% GT executability</strong> — plans look valid but fail in real simulators.
          Only Sim-LAPIS² closes this gap with ground-truth feedback.
        </p>
      </div>
    </div>
  )
}

// ── Live results (from API) ───────────────────────────────────────────────────

function LiveResults() {
  const [data, setData] = useState<ModelRaceData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedDomain, setSelectedDomain] = useState<string>('all')
  const [selectedMetric, setSelectedMetric] = useState<'val_rate' | 'success_rate' | 'avg_plan_length' | 'avg_time'>('val_rate')

  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true)
        const result = await fetchModelRaceData()
        setData(result)
      } catch (e) {
        setError((e as Error).message)
      } finally {
        setIsLoading(false)
      }
    }
    loadData()
  }, [])

  if (isLoading) {
    return (
      <div className="py-12 text-center">
        <div className="inline-flex items-center gap-3 text-lapis-muted">
          <div className="w-5 h-5 border-2 border-lapis-accent border-t-transparent rounded-full animate-spin" />
          <span>Loading live results...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-6 text-center">
        <p className="text-rose-400 font-medium">Error loading results: {error}</p>
      </div>
    )
  }

  if (!data || data.summaries.length === 0) {
    return (
      <div className="bg-lapis-card border border-lapis-border rounded-xl p-8 text-center">
        <Wifi className="w-8 h-8 text-lapis-muted mx-auto mb-3" />
        <p className="text-lapis-muted font-medium">No live results yet.</p>
        <p className="text-sm text-lapis-muted mt-2">Run the pipeline on the Live Execution tab to generate results here.</p>
      </div>
    )
  }

  const filteredSummaries = selectedDomain === 'all'
    ? data.summaries
    : data.summaries.filter((s) => s.domain === selectedDomain)

  const chartData = prepareChartData(filteredSummaries, selectedMetric)
  const overallStats = calculateOverallStats(filteredSummaries)

  return (
    <div className="space-y-6">
      {/* Overall Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={<Award className="w-5 h-5" />} label="Best Method" value={overallStats.bestMethod} color="text-emerald-400" />
        <StatCard icon={<TrendingUp className="w-5 h-5" />} label="Avg Success Rate" value={`${(overallStats.avgSuccessRate * 100).toFixed(1)}%`} color="text-blue-400" />
        <StatCard icon={<Zap className="w-5 h-5" />} label="Total Runs" value={overallStats.totalRuns.toString()} color="text-violet-400" />
        <StatCard icon={<Clock className="w-5 h-5" />} label="Avg Time" value={`${overallStats.avgTime.toFixed(1)}s`} color="text-orange-400" />
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-lapis-text-secondary">Domain:</label>
          <select
            value={selectedDomain}
            onChange={(e) => setSelectedDomain(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-lapis-card border border-lapis-border text-lapis-text text-sm focus:outline-none focus:border-lapis-accent"
          >
            <option value="all">All Domains</option>
            {data.domains.map((domain) => (
              <option key={domain} value={domain}>{domain}</option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-lapis-text-secondary">Metric:</label>
          <div className="flex gap-1 bg-lapis-card border border-lapis-border rounded-lg p-1">
            {(['val_rate', 'success_rate', 'avg_plan_length', 'avg_time'] as const).map((metric) => (
              <MetricButton key={metric} label={getMetricLabel(metric).split(' ')[0]} active={selectedMetric === metric} onClick={() => setSelectedMetric(metric)} />
            ))}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-lapis-card border border-lapis-border rounded-xl p-6">
        <h3 className="text-lg font-semibold text-lapis-text mb-4">{getMetricLabel(selectedMetric)} Comparison</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }} />
            <Legend />
            {data.methods.map((method, idx) => (
              <Bar key={method} dataKey={method} fill={getMethodColor(method, idx)} radius={[4, 4, 0, 0]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Table */}
      <div className="bg-lapis-card border border-lapis-border rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-lapis-border">
          <h3 className="text-lg font-semibold text-lapis-text">Detailed Results</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-lapis-bg/50 text-lapis-muted">
                <th className="px-4 py-3 text-left font-medium">Domain</th>
                <th className="px-4 py-3 text-left font-medium">Method</th>
                <th className="px-4 py-3 text-left font-medium">Model</th>
                <th className="px-4 py-3 text-right font-medium">VAL Rate</th>
                <th className="px-4 py-3 text-right font-medium">Plan SR</th>
                <th className="px-4 py-3 text-right font-medium">GT Exec.</th>
                <th className="px-4 py-3 text-right font-medium">Avg Refs</th>
                <th className="px-4 py-3 text-right font-medium">Avg Time (s)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-lapis-border">
              {filteredSummaries.map((summary, idx) => (
                <tr key={idx} className="hover:bg-lapis-bg/30 transition-colors">
                  <td className="px-4 py-3 text-lapis-text font-medium capitalize">{summary.domain}</td>
                  <td className="px-4 py-3">
                    <span className={cn('px-2 py-1 rounded text-xs font-semibold whitespace-nowrap', getMethodBadgeClass(summary.method))}>
                      {summary.method_label || summary.method}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-lapis-text-secondary text-xs">{summary.model}</td>
                  <td className="px-4 py-3 text-right"><span className={cn('font-semibold', rateColor(summary.val_rate))}>{(summary.val_rate * 100).toFixed(0)}%</span></td>
                  <td className="px-4 py-3 text-right"><span className={cn('font-semibold', rateColor(summary.success_rate))}>{(summary.success_rate * 100).toFixed(0)}%</span></td>
                  <td className="px-4 py-3 text-right">
                    {summary.gt_executability != null
                      ? <span className={cn('font-semibold', rateColor(summary.gt_executability))}>{(summary.gt_executability * 100).toFixed(0)}%</span>
                      : <span className="text-lapis-muted text-xs">—</span>}
                  </td>
                  <td className="px-4 py-3 text-right text-lapis-text-secondary">{summary.avg_refinements.toFixed(1)}</td>
                  <td className="px-4 py-3 text-right text-lapis-text-secondary">{summary.avg_time > 0 ? summary.avg_time.toFixed(1) : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function ModelRace() {
  const [source, setSource] = useState<'paper' | 'live'>('paper')

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      <div className="flex items-baseline justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-lapis-text">Model Race</h1>
          <p className="text-sm text-lapis-muted mt-1">Compare LAPIS against baseline methods across IPC domains</p>
        </div>
        <div className="flex gap-1 bg-lapis-card border border-lapis-border rounded-lg p-1">
          <button
            onClick={() => setSource('paper')}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded text-sm font-medium transition-colors',
              source === 'paper' ? 'bg-lapis-accent text-lapis-bg' : 'text-lapis-text-secondary hover:text-lapis-text'
            )}
          >
            <BookOpen className="w-4 h-4" />
            Paper Results
          </button>
          <button
            onClick={() => setSource('live')}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded text-sm font-medium transition-colors',
              source === 'live' ? 'bg-lapis-accent text-lapis-bg' : 'text-lapis-text-secondary hover:text-lapis-text'
            )}
          >
            <Wifi className="w-4 h-4" />
            Live Results
          </button>
        </div>
      </div>

      {source === 'paper' ? <PaperResultsTable /> : <LiveResults />}
    </div>
  )
}

// ── Helper Components ─────────────────────────────────────────────────────────

function StatCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string; color: string }) {
  return (
    <div className="bg-lapis-card border border-lapis-border rounded-xl p-4">
      <div className="flex items-center gap-3">
        <div className={cn('p-2 rounded-lg bg-lapis-bg/50', color)}>{icon}</div>
        <div>
          <p className="text-xs text-lapis-muted">{label}</p>
          <p className={cn('text-xl font-bold', color)}>{value}</p>
        </div>
      </div>
    </div>
  )
}

function MetricButton({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn('px-3 py-1 rounded text-xs font-medium transition-colors', active ? 'bg-lapis-accent text-lapis-bg' : 'text-lapis-text-secondary hover:text-lapis-text')}
    >
      {label}
    </button>
  )
}

// ── Helper Functions ──────────────────────────────────────────────────────────

function rateColor(rate: number): string {
  if (rate >= 0.9) return 'text-emerald-400'
  if (rate >= 0.7) return 'text-yellow-400'
  if (rate >= 0.4) return 'text-orange-400'
  return 'text-rose-400'
}

type ChartMetric = 'val_rate' | 'success_rate' | 'avg_plan_length' | 'avg_time'

function prepareChartData(summaries: BenchmarkSummary[], metric: ChartMetric) {
  const domainGroups = new Map<string, Record<string, number>>()
  summaries.forEach((s) => {
    if (!domainGroups.has(s.domain)) domainGroups.set(s.domain, {})
    const group = domainGroups.get(s.domain)!
    const raw = s[metric as keyof BenchmarkSummary] as number ?? 0
    group[s.method_label || s.method] = (metric === 'val_rate' || metric === 'success_rate') ? raw * 100 : raw
  })
  return Array.from(domainGroups.entries()).map(([domain, methods]) => ({ name: domain, ...methods }))
}

function calculateOverallStats(summaries: BenchmarkSummary[]) {
  if (summaries.length === 0) return { bestMethod: 'N/A', avgSuccessRate: 0, totalRuns: 0, avgTime: 0 }
  const methodRates = new Map<string, number[]>()
  summaries.forEach((s) => {
    if (!methodRates.has(s.method)) methodRates.set(s.method, [])
    methodRates.get(s.method)!.push(s.success_rate)
  })
  let bestMethod = 'N/A', bestRate = 0
  methodRates.forEach((rates, method) => {
    const avg = rates.reduce((a, b) => a + b, 0) / rates.length
    if (avg > bestRate) { bestRate = avg; bestMethod = method.toUpperCase() }
  })
  return {
    bestMethod,
    avgSuccessRate: summaries.reduce((sum, s) => sum + s.success_rate, 0) / summaries.length,
    totalRuns: summaries.reduce((sum, s) => sum + s.total_runs, 0),
    avgTime: summaries.reduce((sum, s) => sum + s.avg_time, 0) / summaries.length,
  }
}

function getMetricLabel(metric: ChartMetric): string {
  switch (metric) {
    case 'val_rate':        return 'VAL Validation Rate (%)'
    case 'success_rate':    return 'Planning Success Rate (%)'
    case 'avg_plan_length': return 'Average Plan Length'
    case 'avg_time':        return 'Average Generation Time (s)'
  }
}

function getMethodColor(_method: string, idx: number): string {
  return ['#4fc3f7', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'][idx % 5]
}

function getMethodBadgeClass(method: string): string {
  const m = method.toLowerCase()
  if (m.includes('sim'))    return 'bg-amber-500/20 text-amber-300'
  if (m.includes('lapis'))  return 'bg-cyan-500/20 text-cyan-400'
  if (m.includes('llm') || m.includes('llmpp')) return 'bg-violet-500/20 text-violet-400'
  if (m.includes('nl2plan')) return 'bg-emerald-500/20 text-emerald-400'
  return 'bg-slate-500/20 text-slate-400'
}
