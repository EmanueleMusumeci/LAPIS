/**
 * ModelRace - Benchmark comparison dashboard showing multiple methods/models side-by-side.
 */
import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { fetchModelRaceData } from '@/lib/api'
import type { ModelRaceData, BenchmarkSummary } from '@/types'
import { cn } from '@/lib/utils'
import { TrendingUp, Award, Zap, Clock } from 'lucide-react'

export default function ModelRace() {
  const [data, setData] = useState<ModelRaceData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filter state
  const [selectedDomain, setSelectedDomain] = useState<string>('all')
  const [selectedMetric, setSelectedMetric] = useState<'success_rate' | 'avg_plan_length' | 'avg_time'>('success_rate')

  // Load data on mount
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
      <div className="max-w-7xl mx-auto px-4 py-12 text-center">
        <div className="inline-flex items-center gap-3 text-lapis-muted">
          <div className="w-5 h-5 border-2 border-lapis-accent border-t-transparent rounded-full animate-spin" />
          <span>Loading benchmark results...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-6 text-center">
          <p className="text-rose-400 font-medium">Error loading results: {error}</p>
        </div>
      </div>
    )
  }

  if (!data || data.summaries.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="bg-lapis-card border border-lapis-border rounded-xl p-6 text-center">
          <p className="text-lapis-muted">No benchmark results available yet.</p>
          <p className="text-sm text-lapis-muted mt-2">Run benchmarks to see comparison data here.</p>
        </div>
      </div>
    )
  }

  // Filter summaries by domain
  const filteredSummaries = selectedDomain === 'all'
    ? data.summaries
    : data.summaries.filter((s) => s.domain === selectedDomain)

  // Prepare chart data
  const chartData = prepareChartData(filteredSummaries, selectedMetric)

  // Calculate overall stats
  const overallStats = calculateOverallStats(filteredSummaries)

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-baseline justify-between">
        <div>
          <h1 className="text-3xl font-bold text-lapis-text">Model Race</h1>
          <p className="text-sm text-lapis-muted mt-1">
            Compare LAPIS against baseline methods across IPC domains
          </p>
        </div>
      </div>

      {/* Overall Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<Award className="w-5 h-5" />}
          label="Best Method"
          value={overallStats.bestMethod}
          color="text-emerald-400"
        />
        <StatCard
          icon={<TrendingUp className="w-5 h-5" />}
          label="Avg Success Rate"
          value={`${(overallStats.avgSuccessRate * 100).toFixed(1)}%`}
          color="text-blue-400"
        />
        <StatCard
          icon={<Zap className="w-5 h-5" />}
          label="Total Runs"
          value={overallStats.totalRuns.toString()}
          color="text-violet-400"
        />
        <StatCard
          icon={<Clock className="w-5 h-5" />}
          label="Avg Time"
          value={`${overallStats.avgTime.toFixed(1)}s`}
          color="text-orange-400"
        />
      </div>

      {/* Filter Controls */}
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
              <option key={domain} value={domain}>
                {domain}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-lapis-text-secondary">Metric:</label>
          <div className="flex gap-1 bg-lapis-card border border-lapis-border rounded-lg p-1">
            <MetricButton
              label="Success Rate"
              active={selectedMetric === 'success_rate'}
              onClick={() => setSelectedMetric('success_rate')}
            />
            <MetricButton
              label="Plan Length"
              active={selectedMetric === 'avg_plan_length'}
              onClick={() => setSelectedMetric('avg_plan_length')}
            />
            <MetricButton
              label="Time"
              active={selectedMetric === 'avg_time'}
              onClick={() => setSelectedMetric('avg_time')}
            />
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-lapis-card border border-lapis-border rounded-xl p-6">
        <h3 className="text-lg font-semibold text-lapis-text mb-4">
          {getMetricLabel(selectedMetric)} Comparison
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                border: '1px solid #334155',
                borderRadius: '8px',
              }}
            />
            <Legend />
            {data.methods.map((method, idx) => (
              <Bar
                key={method}
                dataKey={method}
                fill={getMethodColor(method, idx)}
                radius={[4, 4, 0, 0]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Table */}
      <div className="bg-lapis-card border border-lapis-border rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-lapis-border">
          <h3 className="text-lg font-semibold text-lapis-text">Detailed Results</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-lapis-bg/50 text-lapis-muted">
                <th className="px-6 py-3 text-left font-medium">Domain</th>
                <th className="px-6 py-3 text-left font-medium">Method</th>
                <th className="px-6 py-3 text-left font-medium">Model</th>
                <th className="px-6 py-3 text-right font-medium">Success Rate</th>
                <th className="px-6 py-3 text-right font-medium">Avg Plan Length</th>
                <th className="px-6 py-3 text-right font-medium">Avg Refinements</th>
                <th className="px-6 py-3 text-right font-medium">Avg Time (s)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-lapis-border">
              {filteredSummaries.map((summary, idx) => (
                <tr key={idx} className="hover:bg-lapis-bg/30 transition-colors">
                  <td className="px-6 py-3 text-lapis-text font-medium">{summary.domain}</td>
                  <td className="px-6 py-3">
                    <span className={cn(
                      'px-2 py-1 rounded text-xs font-semibold',
                      getMethodBadgeClass(summary.method)
                    )}>
                      {summary.method.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-lapis-text-secondary text-xs">{summary.model}</td>
                  <td className="px-6 py-3 text-right">
                    <span className={cn(
                      'font-semibold',
                      summary.success_rate >= 0.8 ? 'text-emerald-400' :
                      summary.success_rate >= 0.5 ? 'text-yellow-400' :
                      'text-rose-400'
                    )}>
                      {(summary.success_rate * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-3 text-right text-lapis-text-secondary">{summary.avg_plan_length.toFixed(1)}</td>
                  <td className="px-6 py-3 text-right text-lapis-text-secondary">{summary.avg_refinements.toFixed(1)}</td>
                  <td className="px-6 py-3 text-right text-lapis-text-secondary">{summary.avg_time.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

// ── Helper Components ─────────────────────────────────────────────────────────

interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: string
  color: string
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  return (
    <div className="bg-lapis-card border border-lapis-border rounded-xl p-4">
      <div className="flex items-center gap-3">
        <div className={cn('p-2 rounded-lg bg-lapis-bg/50', color)}>
          {icon}
        </div>
        <div>
          <p className="text-xs text-lapis-muted">{label}</p>
          <p className={cn('text-xl font-bold', color)}>{value}</p>
        </div>
      </div>
    </div>
  )
}

interface MetricButtonProps {
  label: string
  active: boolean
  onClick: () => void
}

function MetricButton({ label, active, onClick }: MetricButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'px-3 py-1 rounded text-xs font-medium transition-colors',
        active
          ? 'bg-lapis-accent text-lapis-bg'
          : 'text-lapis-text-secondary hover:text-lapis-text'
      )}
    >
      {label}
    </button>
  )
}

// ── Helper Functions ──────────────────────────────────────────────────────────

type ChartMetric = 'success_rate' | 'avg_plan_length' | 'avg_time'

function prepareChartData(summaries: BenchmarkSummary[], metric: ChartMetric) {
  // Group by domain, then pivot by method
  const domainGroups = new Map<string, Record<string, number>>()

  summaries.forEach((s) => {
    if (!domainGroups.has(s.domain)) {
      domainGroups.set(s.domain, {})
    }
    const group = domainGroups.get(s.domain)!
    group[s.method] = metric === 'success_rate' ? s[metric] * 100 : s[metric]
  })

  return Array.from(domainGroups.entries()).map(([domain, methods]) => ({
    name: domain,
    ...methods,
  }))
}

function calculateOverallStats(summaries: BenchmarkSummary[]) {
  if (summaries.length === 0) {
    return {
      bestMethod: 'N/A',
      avgSuccessRate: 0,
      totalRuns: 0,
      avgTime: 0,
    }
  }

  // Best method by success rate
  const methodSuccessRates = new Map<string, number[]>()
  summaries.forEach((s) => {
    if (!methodSuccessRates.has(s.method)) {
      methodSuccessRates.set(s.method, [])
    }
    methodSuccessRates.get(s.method)!.push(s.success_rate)
  })

  let bestMethod = 'N/A'
  let bestRate = 0
  methodSuccessRates.forEach((rates, method) => {
    const avg = rates.reduce((a, b) => a + b, 0) / rates.length
    if (avg > bestRate) {
      bestRate = avg
      bestMethod = method.toUpperCase()
    }
  })

  const totalRuns = summaries.reduce((sum, s) => sum + s.total_runs, 0)
  const avgSuccessRate = summaries.reduce((sum, s) => sum + s.success_rate, 0) / summaries.length
  const avgTime = summaries.reduce((sum, s) => sum + s.avg_time, 0) / summaries.length

  return { bestMethod, avgSuccessRate, totalRuns, avgTime }
}

function getMetricLabel(metric: ChartMetric): string {
  switch (metric) {
    case 'success_rate':
      return 'Success Rate (%)'
    case 'avg_plan_length':
      return 'Average Plan Length'
    case 'avg_time':
      return 'Average Execution Time (s)'
  }
}

function getMethodColor(_method: string, idx: number): string {
  const colors = ['#4fc3f7', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
  return colors[idx % colors.length]
}

function getMethodBadgeClass(method: string): string {
  if (method.toLowerCase().includes('lapis')) {
    return 'bg-cyan-500/20 text-cyan-400'
  }
  if (method.toLowerCase().includes('llmpp')) {
    return 'bg-violet-500/20 text-violet-400'
  }
  if (method.toLowerCase().includes('nl2plan')) {
    return 'bg-emerald-500/20 text-emerald-400'
  }
  return 'bg-slate-500/20 text-slate-400'
}
