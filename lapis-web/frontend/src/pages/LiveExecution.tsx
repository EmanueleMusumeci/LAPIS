/**
 * LiveExecution - Main page for live pipeline execution with real-time updates.
 */
import { useState } from 'react'
import { usePipeline } from '@/hooks/usePipeline'
import { usePresets } from '@/hooks/usePresets'
import type { Preset } from '@/types'
import {
  PresetSelector,
  ConfigPanel,
  PipelineProgress,
  StageCard,
  PlanTrace,
  PDDLViewer,
} from '@/components'
import { Loader2, Play, RotateCcw, Wifi, WifiOff } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { PipelineConfig, PipelineMethod } from '@/types'

export default function LiveExecution() {
  const {
    connectionStatus,
    isRunning,
    stages,
    result,
    error,
    runPipeline,
    reset,
    connect,
  } = usePipeline()

  const { data: presetsData } = usePresets()

  // Configuration state
  const [selectedPreset, setSelectedPreset] = useState<Preset | null>(null)
  const [method, setMethod] = useState<PipelineMethod>('lapis')
  const [modelId, setModelId] = useState('claude-sonnet-4-6')
  const [plannerName, setPlannerName] = useState('up_fd')
  const [maxRefinements, setMaxRefinements] = useState(3)
  const [plannerTimeout, setPlannerTimeout] = useState(300)
  const [skipAdequacy, setSkipAdequacy] = useState(false)
  const [semanticChecks] = useState(true)
  const [refineDomain] = useState(true)
  const [extractorType] = useState('auto')

  // NL inputs (populated from preset or manual entry)
  const [domainNL, setDomainNL] = useState('')
  const [problemNL, setProblemNL] = useState('')
  const [domainName, setDomainName] = useState('')

  // Handle preset selection
  const handlePresetChange = (preset: Preset | null) => {
    console.log('[LAPIS] Preset selected:', preset)
    setSelectedPreset(preset)
    if (preset) {
      setDomainNL(preset.domain_nl)
      setProblemNL(preset.problem_nl)
      setDomainName(preset.domain)
      console.log('[LAPIS] Fields set:', {
        domainNL: preset.domain_nl?.slice(0, 50),
        problemNL: preset.problem_nl?.slice(0, 50),
        domainName: preset.domain,
      })
    }
  }

  // Handle pipeline execution
  const handleRun = () => {
    console.log('[LAPIS] handleRun called', { domainNL, problemNL, domainName, connectionStatus })

    if (!domainNL || !problemNL || !domainName) {
      alert('Please provide domain name, domain NL, and problem NL')
      return
    }

    const config: PipelineConfig = {
      domain_nl: domainNL,
      problem_nl: problemNL,
      method,
      domain_name: domainName,
      model_id: modelId,
      planner_name: plannerName,
      planner_timeout: plannerTimeout,
      max_refinements: maxRefinements,
      skip_adequacy: skipAdequacy,
      semantic_checks: semanticChecks,
      refine_domain: refineDomain,
      extractor_type: extractorType,
    }

    console.log('[LAPIS] Running pipeline with config:', config)
    runPipeline(config)
  }

  const isConnected = connectionStatus === 'connected'
  const canRun = isConnected && !isRunning && domainNL && problemNL && domainName
  const currentRunningStage = stages.find((stage) => stage.status === 'running')

  const executionStatus = (() => {
    if (isRunning && currentRunningStage) {
      return {
        label: `Running: ${currentRunningStage.name}`,
        detail: currentRunningStage.adequacy_analysis || 'Processing current stage...',
      }
    }

    if (isRunning) {
      return {
        label: 'Starting pipeline...',
        detail: 'Request sent. Waiting for first stage update from backend.',
      }
    }

    if (result?.success) {
      return {
        label: 'Pipeline completed',
        detail: `Finished in ${result.total_time.toFixed(2)}s with ${result.refinements} refinements.`,
      }
    }

    if (result && !result.success) {
      return {
        label: 'Pipeline failed',
        detail: result.error_msg || 'Execution ended with an error.',
      }
    }

    return {
      label: isConnected ? 'Ready to run' : 'Waiting for server connection',
      detail: isConnected
        ? 'Configure inputs and click Run Pipeline.'
        : 'The UI will enable execution automatically once WebSocket connects.',
    }
  })()

  // Debug: log state changes
  console.log('[LAPIS] State:', {
    connectionStatus,
    isConnected,
    isRunning,
    canRun,
    domainName: domainName?.slice(0, 20),
    domainNL: domainNL ? `${domainNL.length} chars` : 'empty',
    problemNL: problemNL ? `${problemNL.length} chars` : 'empty',
    selectedPreset: selectedPreset?.id,
  })

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      {/* Connection Status Bar */}
      <div
        className={cn(
          'flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors',
          isConnected
            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
            : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
        )}
      >
        <div className="flex items-center gap-2">
          {isConnected ? (
            <>
              <Wifi className="w-4 h-4" />
              <span>Connected to server</span>
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4" />
              <span>
                {connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected from server'}
              </span>
            </>
          )}
        </div>
        {!isConnected && connectionStatus !== 'connecting' && (
          <button
            onClick={connect}
            className="px-3 py-1 text-xs font-medium bg-rose-500/20 hover:bg-rose-500/30 rounded transition-colors"
          >
            Reconnect
          </button>
        )}
      </div>

      {/* Main Layout: Config + Execution */}
      <div className="grid lg:grid-cols-[320px_1fr] gap-6">
        {/* Left Column: Configuration */}
        <div className="space-y-4">
          {/* Preset Selector */}
          <div className="bg-lapis-card border border-lapis-border rounded-xl p-4 space-y-3">
            <h3 className="text-sm font-semibold text-lapis-text">Select Preset</h3>
            <PresetSelector
              presets={presetsData?.presets || []}
              selectedPreset={selectedPreset}
              onPresetChange={handlePresetChange}
            />
          </div>

          {/* Configuration Panel */}
          <div className="bg-lapis-card border border-lapis-border rounded-xl p-4 space-y-3">
            <h3 className="text-sm font-semibold text-lapis-text">Configuration</h3>
            <ConfigPanel
              method={method}
              onMethodChange={setMethod}
              modelId={modelId}
              onModelChange={setModelId}
              plannerName={plannerName}
              onPlannerChange={setPlannerName}
              maxRefinements={maxRefinements}
              onRefinementsChange={setMaxRefinements}
              plannerTimeout={plannerTimeout}
              onTimeoutChange={setPlannerTimeout}
              skipAdequacy={skipAdequacy}
              onSkipAdequacyChange={setSkipAdequacy}
            />
          </div>

          {/* Action Buttons */}
          <div className="space-y-2">
            <button
              onClick={handleRun}
              disabled={!canRun}
              className={cn(
                'w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all',
                canRun
                  ? 'bg-lapis-accent text-lapis-bg hover:bg-lapis-accent/90 shadow-lg shadow-lapis-accent/30'
                  : 'bg-lapis-card border border-lapis-border text-lapis-text-secondary cursor-not-allowed'
              )}
            >
              {isRunning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              <span>{isRunning ? 'Running...' : 'Run Pipeline'}</span>
            </button>

            {/* Show why button is disabled */}
            {!canRun && !isRunning && (
              <p className="text-xs text-lapis-muted text-center">
                {!isConnected
                  ? 'Connecting to server...'
                  : !domainName || !domainNL || !problemNL
                  ? 'Select a preset or fill in custom task description'
                  : ''}
              </p>
            )}

            {(result || error) && (
              <button
                onClick={reset}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg border border-lapis-border text-lapis-text-secondary hover:border-lapis-accent/50 hover:text-lapis-text transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Reset</span>
              </button>
            )}
          </div>
        </div>

        {/* Right Column: Execution & Results */}
        <div className="space-y-4">
          {/* Execution Status */}
          <div
            className={cn(
              'rounded-xl border p-4',
              isRunning
                ? 'bg-blue-500/10 border-blue-500/30'
                : result?.success
                ? 'bg-emerald-500/10 border-emerald-500/30'
                : result
                ? 'bg-rose-500/10 border-rose-500/30'
                : 'bg-lapis-card border-lapis-border'
            )}
          >
            <div className="flex items-start gap-3">
              {isRunning ? (
                <Loader2 className="w-4 h-4 mt-0.5 animate-spin text-blue-300" />
              ) : (
                <Play className="w-4 h-4 mt-0.5 text-lapis-muted" />
              )}
              <div className="space-y-1">
                <p className="text-sm font-semibold text-lapis-text">{executionStatus.label}</p>
                <p className="text-xs text-lapis-text-secondary whitespace-pre-wrap">{executionStatus.detail}</p>
              </div>
            </div>
          </div>

          {/* Custom NL Input (editable when no preset or custom selected) */}
          {!selectedPreset && (
            <div className="bg-lapis-card border border-lapis-border rounded-xl p-4 space-y-4">
              <h3 className="text-sm font-semibold text-lapis-text">Custom Task Description</h3>

              {/* Domain Name */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-lapis-muted">Domain Name</label>
                <input
                  type="text"
                  value={domainName}
                  onChange={(e) => setDomainName(e.target.value)}
                  placeholder="e.g., blocksworld, gripper, logistics"
                  className="w-full px-3 py-2 rounded-lg bg-lapis-bg border border-lapis-border text-lapis-text text-sm focus:outline-none focus:border-lapis-accent"
                />
              </div>

              {/* Domain NL */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-lapis-muted">Domain Description (Natural Language)</label>
                <textarea
                  value={domainNL}
                  onChange={(e) => setDomainNL(e.target.value)}
                  placeholder="Describe the domain in natural language..."
                  rows={4}
                  className="w-full px-3 py-2 rounded-lg bg-lapis-bg border border-lapis-border text-lapis-text text-sm font-mono focus:outline-none focus:border-lapis-accent resize-none"
                />
              </div>

              {/* Problem NL */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-lapis-muted">Problem Description (Natural Language)</label>
                <textarea
                  value={problemNL}
                  onChange={(e) => setProblemNL(e.target.value)}
                  placeholder="Describe the problem (initial state and goal)..."
                  rows={6}
                  className="w-full px-3 py-2 rounded-lg bg-lapis-bg border border-lapis-border text-lapis-text text-sm font-mono focus:outline-none focus:border-lapis-accent resize-none"
                />
              </div>
            </div>
          )}

          {/* NL Inputs (read-only display when preset is selected) */}
          {selectedPreset && (domainNL || problemNL) && (
            <div className="bg-lapis-card border border-lapis-border rounded-xl p-4 space-y-3">
              <h3 className="text-sm font-semibold text-lapis-text">Task Description</h3>
              {domainNL && (
                <div className="space-y-1">
                  <label className="text-xs font-medium text-lapis-muted">Domain</label>
                  <div className="text-sm text-lapis-text-secondary bg-lapis-bg/50 rounded p-2 font-mono text-xs whitespace-pre-wrap">
                    {domainNL}
                  </div>
                </div>
              )}
              {problemNL && (
                <div className="space-y-1">
                  <label className="text-xs font-medium text-lapis-muted">Problem</label>
                  <div className="text-sm text-lapis-text-secondary bg-lapis-bg/50 rounded p-2 font-mono text-xs whitespace-pre-wrap">
                    {problemNL}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4">
              <p className="text-sm font-medium text-rose-400">Error: {error}</p>
            </div>
          )}

          {/* Pipeline Progress */}
          {stages.length > 0 && (
            <div className="space-y-4">
              <PipelineProgress stages={stages} />

              {/* Stage Cards */}
              <div className="space-y-2">
                {stages.map((stage) => (
                  <StageCard key={stage.name} stage={stage} />
                ))}
              </div>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="space-y-4">
              {/* Success Banner */}
              <div
                className={cn(
                  'px-4 py-3 rounded-xl font-semibold text-center',
                  result.success
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                )}
              >
                {result.success ? '✓ Pipeline Complete' : '✗ Pipeline Failed'}
                <span className="ml-3 text-sm font-normal opacity-80">
                  ({result.total_time.toFixed(2)}s, {result.refinements} refinements)
                </span>
              </div>

              {/* Plan Trace */}
              {result.plan_actions.length > 0 && (
                <div className="bg-lapis-card border border-lapis-border rounded-xl p-4 space-y-3">
                  <h3 className="text-sm font-semibold text-lapis-text">Generated Plan</h3>
                  <PlanTrace
                    actions={result.plan_actions}
                    stepImages={result.plan_step_images}
                    animationUrl={result.plan_animation_url}
                  />
                </div>
              )}

              {/* PDDL Outputs */}
              <div className="grid md:grid-cols-2 gap-4">
                {result.final_domain_pddl && (
                  <div className="bg-lapis-card border border-lapis-border rounded-xl p-4 space-y-3">
                    <h3 className="text-sm font-semibold text-lapis-text">Domain PDDL</h3>
                    <PDDLViewer code={result.final_domain_pddl} />
                  </div>
                )}

                {result.final_problem_pddl && (
                  <div className="bg-lapis-card border border-lapis-border rounded-xl p-4 space-y-3">
                    <h3 className="text-sm font-semibold text-lapis-text">Problem PDDL</h3>
                    <PDDLViewer code={result.final_problem_pddl} />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
