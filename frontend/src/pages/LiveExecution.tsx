/**
 * LiveExecution - Main page for live pipeline execution with real-time updates.
 */
import { useState, useEffect } from 'react'
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
import { Loader2, Play, RotateCcw, Wifi, WifiOff, StopCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { PipelineConfig, PipelineMethod } from '@/types'
import { useApiKey, ApiKeyInput } from '@/contexts/ApiKeyContext'
import { simulateFrames, type SimFramesResult } from '@/lib/api'

export default function LiveExecution() {
  const {
    connectionStatus,
    isRunning,
    stages,
    result,
    error,
    runPipeline,
    cancelPipeline,
    reset,
    connect,
  } = usePipeline()

  const { data: presetsData } = usePresets()
  const { apiKey } = useApiKey()

  // Configuration state
  const [selectedPreset, setSelectedPreset] = useState<Preset | null>(null)
  const [method, setMethod] = useState<PipelineMethod>('lapis')
  const [modelId, setModelId] = useState('claude-sonnet-4-6')
  const [plannerName, setPlannerName] = useState('up_fd')
  const [maxRefinements, setMaxRefinements] = useState(3)
  const [plannerTimeout, setPlannerTimeout] = useState(300)
  const [skipAdequacy, setSkipAdequacy] = useState(false)
  const [semanticChecks, setSemanticChecks] = useState(true)
  const [refineDomain] = useState(true)
  const [extractorType] = useState('auto')

  // NL inputs (populated from preset or manual entry)
  const [domainNL, setDomainNL] = useState('')
  const [problemNL, setProblemNL] = useState('')
  const [domainName, setDomainName] = useState('')
  const [simFrames, setSimFrames] = useState<SimFramesResult | null>(null)

  // When a pipeline result arrives with a plan, fetch graphical frames
  useEffect(() => {
    if (!result?.plan_actions?.length || !result.final_domain_pddl || !result.final_problem_pddl) {
      setSimFrames(null)
      return
    }
    let cancelled = false
    simulateFrames({
      domain_pddl: result.final_domain_pddl,
      problem_pddl: result.final_problem_pddl,
      plan: result.plan_actions,
      domain_name: domainName,
    }).then((frames) => {
      if (!cancelled && frames.success && frames.frames.length > 0) setSimFrames(frames)
    }).catch(() => {})
    return () => { cancelled = true }
  }, [result, domainName])

  // Handle preset selection — populate fields, mark as preset
  const handlePresetChange = (preset: Preset | null) => {
    setSelectedPreset(preset)
    if (preset) {
      setDomainNL(preset.domain_nl)
      setProblemNL(preset.problem_nl)
      setDomainName(preset.domain)
    }
  }

  // Editing any NL field switches back to Custom
  const handleDomainNameChange = (v: string) => { setDomainName(v); setSelectedPreset(null) }
  const handleDomainNLChange   = (v: string) => { setDomainNL(v);   setSelectedPreset(null) }
  const handleProblemNLChange  = (v: string) => { setProblemNL(v);  setSelectedPreset(null) }

  // Run / re-run pipeline
  const handleRun = () => {
    if (!domainNL || !problemNL || !domainName) {
      alert('Please provide domain name, domain description, and problem description.')
      return
    }

    // Clear previous run results immediately so UI reflects new run
    if (result || error) reset()

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
      api_key: apiKey || undefined,
    }
    runPipeline(config)
  }

  const isConnected = connectionStatus === 'connected'
  const hasInputs = !!(domainNL && problemNL && domainName)
  const canRun = isConnected && !isRunning && hasInputs
  const serverOffline = !isConnected
  const offlineTitle = serverOffline ? 'Not connected to server' : undefined

  const currentRunningStage = stages.find((stage) => stage.status === 'running')

  const executionStatus = (() => {
    if (isRunning && currentRunningStage) {
      return {
        label: `Running: ${currentRunningStage.name}`,
        detail: currentRunningStage.adequacy_analysis || 'Processing current stage...',
        color: 'bg-blue-500/10 border-blue-500/30',
      }
    }
    if (isRunning) {
      return {
        label: 'Starting pipeline...',
        detail: 'Waiting for first stage update from backend.',
        color: 'bg-blue-500/10 border-blue-500/30',
      }
    }
    if (result?.success) {
      return {
        label: 'Pipeline completed',
        detail: `Finished in ${result.total_time.toFixed(2)}s · ${result.refinements} refinements`,
        color: 'bg-emerald-500/10 border-emerald-500/30',
      }
    }
    if (result) {
      return {
        label: 'Pipeline failed',
        detail: result.error_msg || 'Execution ended with an error.',
        color: 'bg-rose-500/10 border-rose-500/30',
      }
    }
    return {
      label: isConnected ? 'Ready to run' : 'Waiting for server connection',
      detail: isConnected
        ? 'Configure inputs and click Run Pipeline.'
        : 'WebSocket will connect automatically. Check server status if this persists.',
      color: 'bg-lapis-card border-lapis-border',
    }
  })()

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
            <><Wifi className="w-4 h-4" /><span>Connected to server</span></>
          ) : (
            <><WifiOff className="w-4 h-4" /><span>
              {connectionStatus === 'connecting' ? 'Connecting to server...' : 'Disconnected — server unreachable'}
            </span></>
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

      {/* Main Layout */}
      <div className="grid lg:grid-cols-[320px_1fr] gap-6">
        {/* Left Column */}
        <div className="space-y-4">
          {/* Preset Selector */}
          <div
            className={cn(
              'bg-lapis-card border border-lapis-border rounded-xl p-4 space-y-3',
              serverOffline && 'opacity-50 pointer-events-none'
            )}
            title={offlineTitle}
          >
            <h3 className="text-sm font-semibold text-lapis-text">Select Preset</h3>
            <PresetSelector
              presets={presetsData?.presets || []}
              selectedPreset={selectedPreset}
              onPresetChange={handlePresetChange}
            />
          </div>

          {/* API Key */}
          <div className="bg-lapis-card border border-lapis-border rounded-xl p-4">
            <ApiKeyInput />
            <p className="text-xs text-lapis-muted mt-2">
              Leave blank to use the server's API key.
            </p>
          </div>

          {/* Configuration */}
          <div
            className={cn(
              'bg-lapis-card border border-lapis-border rounded-xl p-4 space-y-3',
              serverOffline && 'opacity-50 pointer-events-none'
            )}
            title={offlineTitle}
          >
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
              semanticChecks={semanticChecks}
              onSemanticChecksChange={setSemanticChecks}
            />
          </div>

          {/* Action Buttons */}
          <div className="space-y-2">
            {isRunning ? (
              <button
                onClick={cancelPipeline}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/40 hover:bg-rose-500/30 transition-all"
              >
                <StopCircle className="w-4 h-4" />
                <span>Cancel Pipeline</span>
              </button>
            ) : (
              <button
                onClick={handleRun}
                disabled={!canRun}
                title={
                  !isConnected ? 'Not connected to server' :
                  !hasInputs ? 'Fill in domain name and descriptions' :
                  undefined
                }
                className={cn(
                  'w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all',
                  canRun
                    ? 'bg-lapis-accent text-lapis-bg hover:bg-lapis-accent/90 shadow-lg shadow-lapis-accent/30'
                    : 'bg-lapis-card border border-lapis-border text-lapis-text-secondary cursor-not-allowed'
                )}
              >
                <Play className="w-4 h-4" />
                <span>{result ? 'Run Again' : 'Run Pipeline'}</span>
              </button>
            )}

            {/* Hint why disabled */}
            {!isRunning && !canRun && (
              <p className="text-xs text-lapis-muted text-center">
                {!isConnected ? 'Connecting to server...' :
                 !hasInputs ? 'Select a preset or fill in the task description' : ''}
              </p>
            )}

            {(result || error) && !isRunning && (
              <button
                onClick={reset}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg border border-lapis-border text-lapis-text-secondary hover:border-lapis-accent/50 hover:text-lapis-text transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Clear Results</span>
              </button>
            )}
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-4">
          {/* Execution Status */}
          <div className={cn('rounded-xl border p-4', executionStatus.color)}>
            <div className="flex items-start gap-3">
              {isRunning
                ? <Loader2 className="w-4 h-4 mt-0.5 animate-spin text-blue-300" />
                : <Play className="w-4 h-4 mt-0.5 text-lapis-muted" />
              }
              <div className="space-y-1">
                <p className="text-sm font-semibold text-lapis-text">{executionStatus.label}</p>
                <p className="text-xs text-lapis-text-secondary">{executionStatus.detail}</p>
              </div>
            </div>
          </div>

          {/* Task Description — always editable; preset-loaded shows badge */}
          <div className="bg-lapis-card border border-lapis-border rounded-xl p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-lapis-text">Task Description</h3>
              {selectedPreset && (
                <span className="text-xs text-lapis-muted bg-lapis-bg/60 px-2 py-0.5 rounded">
                  {selectedPreset.id} — edit to customise
                </span>
              )}
            </div>

            {/* Domain Name */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-lapis-muted">Domain Name</label>
              <input
                type="text"
                value={domainName}
                onChange={(e) => handleDomainNameChange(e.target.value)}
                disabled={serverOffline}
                title={offlineTitle}
                placeholder="e.g., blocksworld, gripper, logistics"
                className="w-full px-3 py-2 rounded-lg bg-lapis-bg border border-lapis-border text-lapis-text text-sm focus:outline-none focus:border-lapis-accent disabled:opacity-50"
              />
            </div>

            {/* Domain NL */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-lapis-muted">Domain Description</label>
              <textarea
                value={domainNL}
                onChange={(e) => handleDomainNLChange(e.target.value)}
                disabled={serverOffline}
                title={offlineTitle}
                placeholder="Describe the domain in natural language..."
                rows={4}
                className="w-full px-3 py-2 rounded-lg bg-lapis-bg border border-lapis-border text-lapis-text text-sm font-mono focus:outline-none focus:border-lapis-accent resize-none disabled:opacity-50"
              />
            </div>

            {/* Problem NL */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-lapis-muted">Problem Description</label>
              <textarea
                value={problemNL}
                onChange={(e) => handleProblemNLChange(e.target.value)}
                disabled={serverOffline}
                title={offlineTitle}
                placeholder="Describe the initial state and goal..."
                rows={5}
                className="w-full px-3 py-2 rounded-lg bg-lapis-bg border border-lapis-border text-lapis-text text-sm font-mono focus:outline-none focus:border-lapis-accent resize-none disabled:opacity-50"
              />
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4">
              <p className="text-sm font-medium text-rose-400">Error: {error}</p>
            </div>
          )}

          {/* Pipeline Progress + Stage Cards */}
          {stages.length > 0 && (
            <div className="space-y-4">
              <PipelineProgress stages={stages} />
              <div className="space-y-2">
                {stages.map((stage, idx) => {
                  // Find previous domain/problem PDDL from earlier stages
                  const prevDomains = stages.slice(0, idx).map((s) => s.domain_pddl).filter(Boolean)
                  const prevProblems = stages.slice(0, idx).map((s) => s.problem_pddl).filter(Boolean)
                  const prevDomainPddl = prevDomains[prevDomains.length - 1]
                  const prevProblemPddl = prevProblems[prevProblems.length - 1]
                  return (
                    <StageCard
                      key={stage.name}
                      stage={stage}
                      prevDomainPddl={prevDomainPddl}
                      prevProblemPddl={prevProblemPddl}
                    />
                  )
                })}
              </div>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="space-y-4">
              <div className={cn(
                'px-4 py-3 rounded-xl font-semibold text-center',
                result.success
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
              )}>
                {result.success ? '✓ Pipeline Complete' : '✗ Pipeline Failed'}
                <span className="ml-3 text-sm font-normal opacity-80">
                  ({result.total_time.toFixed(2)}s, {result.refinements} refinements)
                </span>
              </div>

              {result.plan_actions.length > 0 && (
                <div className="bg-lapis-card border border-lapis-border rounded-xl p-4 space-y-3">
                  <h3 className="text-sm font-semibold text-lapis-text">Generated Plan</h3>
                  <PlanTrace
                    actions={result.plan_actions}
                    stepImages={result.plan_step_images}
                    animationUrl={result.plan_animation_url}
                    problemPddl={result.final_problem_pddl}
                    domainName={domainName}
                    simFrames={simFrames ?? undefined}
                  />
                </div>
              )}

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
