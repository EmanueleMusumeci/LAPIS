/**
 * PlanTrace - Interactive plan step-through component.
 *
 * Features:
 * - Slider navigation (1 to N steps)
 * - Prev/Next buttons
 * - Current action banner
 * - Full action list with active highlighting
 * - Blocksworld: client-side tower simulator (no backend needed)
 * - Other IPC domains: state-diff viewer (facts added/removed per step)
 */
import { useState, useMemo } from 'react'
import { ChevronLeft, ChevronRight, CheckCircle2 } from 'lucide-react'
import * as Slider from '@radix-ui/react-slider'
import { cn } from '@/lib/utils'
import {
  normalizeAction,
  parseBWInitState,
  computeStateSequence,
  rebuildBWInit,
} from '@/lib/blocksworldSim'
import BlocksworldEditor from '@/components/editors/BlocksworldEditor'
import type { SimStepsResult, SimFramesResult } from '@/lib/api'

interface PlanTraceProps {
  actions: string[]
  stepImages?: string[]   // Optional: URL to image for each step
  animationUrl?: string   // Optional: URL to full animation GIF
  /** Optional: problem PDDL for client-side BW simulator */
  problemPddl?: string
  /** Optional: domain name for choosing the right simulator */
  domainName?: string
  /** Optional: pre-computed per-step state diffs from backend */
  simSteps?: SimStepsResult
  /** Optional: pre-rendered graphical frames from backend (index 0 = init, i+1 = after action i) */
  simFrames?: SimFramesResult
  className?: string
}

// ─── Blocksworld inline simulator ────────────────────────────────────────────

function BlocksworldSim({
  problemPddl,
  actions,
  step,
}: {
  problemPddl: string
  actions: string[]
  step: number
}) {
  const stateSequence = useMemo(() => {
    const init = parseBWInitState(problemPddl)
    return computeStateSequence(init, actions)
  }, [problemPddl, actions])

  const stateAtStep = stateSequence[step] ?? stateSequence[stateSequence.length - 1]
  const problemAtStep = rebuildBWInit(problemPddl, stateAtStep)

  return (
    <div className="rounded-lg border border-lapis-border overflow-hidden">
      <BlocksworldEditor problemPddl={problemAtStep} onChange={() => {}} readOnly />
    </div>
  )
}

// ─── Generic state-diff viewer ────────────────────────────────────────────────

/** Renders the inner content of a diff step (shared by collapsible and standalone modes). */
function SimDiffContent({
  simSteps,
  step,
  goalFacts,
  showAll,
  setShowAll,
}: {
  simSteps: SimStepsResult
  step: number
  goalFacts: string[]
  showAll: boolean
  setShowAll: (fn: (s: boolean) => boolean) => void
}) {
  if (step === 0) {
    return (
      <>
        <p className="text-lapis-text-secondary uppercase tracking-wide font-medium">Initial State</p>
        <FactList facts={simSteps.init_facts} goalFacts={goalFacts} />
        {goalFacts.length > 0 && (
          <div className="pt-1 border-t border-lapis-border">
            <p className="text-lapis-text-secondary uppercase tracking-wide font-medium mb-1">Goal</p>
            <FactList facts={goalFacts} goalFacts={goalFacts} alwaysHighlight />
          </div>
        )}
      </>
    )
  }

  const stepData = simSteps.steps[step - 1]
  if (!stepData) return null
  const goalReached = step === simSteps.steps.length && simSteps.goal_reached

  return (
    <>
      {goalReached && (
        <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
          <CheckCircle2 className="w-3.5 h-3.5" />
          Goal reached
        </div>
      )}
      {stepData.added.length > 0 && (
        <div>
          <p className="text-emerald-400 uppercase tracking-wide font-medium mb-1">+ Added</p>
          <div className="space-y-0.5">
            {stepData.added.map((f, i) => (
              <div key={i} className="font-mono text-emerald-300 bg-emerald-900/20 rounded px-2 py-0.5">{f}</div>
            ))}
          </div>
        </div>
      )}
      {stepData.removed.length > 0 && (
        <div>
          <p className="text-red-400 uppercase tracking-wide font-medium mb-1">− Removed</p>
          <div className="space-y-0.5">
            {stepData.removed.map((f, i) => (
              <div key={i} className="font-mono text-red-300 bg-red-900/20 rounded px-2 py-0.5 line-through opacity-70">{f}</div>
            ))}
          </div>
        </div>
      )}
      {stepData.added.length === 0 && stepData.removed.length === 0 && (
        <p className="text-lapis-text-secondary italic">No state change (precondition check failed?)</p>
      )}
      <div className="pt-1 border-t border-lapis-border">
        <button
          type="button"
          className="text-lapis-text-secondary hover:text-lapis-text text-xs flex items-center gap-1"
          onClick={() => setShowAll((s) => !s)}
        >
          {showAll ? '▾' : '▸'} All facts ({stepData.all_facts.length})
        </button>
        {showAll && <FactList facts={stepData.all_facts} goalFacts={goalFacts} />}
      </div>
    </>
  )
}

function SimDiffViewer({
  simSteps,
  step,
  collapsible = false,
}: {
  simSteps: SimStepsResult
  step: number   // 1-based step index (0 = init state)
  collapsible?: boolean
}) {
  const [showAll, setShowAll] = useState(false)
  const [collapsed, setCollapsed] = useState(collapsible)

  const goalFacts = simSteps.goal_facts

  // When used as supplementary (below graphical frames), wrap in a collapsible shell
  if (collapsible) {
    return (
      <div className="rounded-lg border border-lapis-border bg-lapis-card/60 text-xs">
        <button
          type="button"
          className="w-full flex items-center gap-1.5 px-3 py-2 text-lapis-text-secondary hover:text-lapis-text"
          onClick={() => setCollapsed((c) => !c)}
        >
          {collapsed ? '▸' : '▾'}
          <span className="font-medium uppercase tracking-wide">State diff</span>
        </button>
        {!collapsed && (
          <div className="px-3 pb-3 space-y-2">
            <SimDiffContent simSteps={simSteps} step={step} goalFacts={goalFacts} showAll={showAll} setShowAll={setShowAll} />
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-lapis-border bg-lapis-card/60 p-3 space-y-2 text-xs">
      <SimDiffContent simSteps={simSteps} step={step} goalFacts={goalFacts} showAll={showAll} setShowAll={setShowAll} />
    </div>
  )
}

function FactList({
  facts,
  goalFacts,
  alwaysHighlight = false,
}: {
  facts: string[]
  goalFacts: string[]
  alwaysHighlight?: boolean
}) {
  const goalSet = new Set(goalFacts.map((f) => f.toLowerCase()))
  return (
    <div className="space-y-0.5 max-h-40 overflow-y-auto">
      {facts.map((f, i) => {
        const isGoal = alwaysHighlight || goalSet.has(f.toLowerCase())
        return (
          <div
            key={i}
            className={cn(
              'font-mono rounded px-2 py-0.5',
              isGoal
                ? 'text-emerald-300 bg-emerald-900/20'
                : 'text-lapis-text bg-lapis-bg/60'
            )}
          >
            {f}
          </div>
        )
      })}
    </div>
  )
}

// ─── Main component ───────────────────────────────────────────────────────────

export function PlanTrace({ actions, stepImages, animationUrl, problemPddl, domainName, simSteps, simFrames, className }: PlanTraceProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [showAnimation, setShowAnimation] = useState(false)

  // Normalize all actions once
  const normalizedActions = useMemo(() => actions.map(normalizeAction), [actions])

  const n = normalizedActions.length
  const hasImages = stepImages && stepImages.length === n
  const currentImage = hasImages ? stepImages[currentStep] : null

  if (n === 0) {
    return (
      <div className={cn('text-center text-lapis-muted py-4', className)}>
        No plan actions to display.
      </div>
    )
  }

  const handlePrev = () => setCurrentStep((prev) => Math.max(0, prev - 1))
  const handleNext = () => setCurrentStep((prev) => Math.min(n - 1, prev + 1))

  const currentAction = normalizedActions[currentStep]
  const clean = currentAction.replace(/^\(|\)$/g, '').trim()
  const parts = clean.split(/\s+/)
  const name = parts[0] || ''
  const params = parts.slice(1)

  const showBWSim = domainName === 'blocksworld' && problemPddl
  // Show graphical frames when available and not blocksworld (has its own client-side sim)
  const showSimFrames = !showBWSim && simFrames?.success && simFrames.frames.length > 0
  // Show sim diff for any domain when simSteps are available, not blocksworld, and no graphical frames
  const showSimDiff = !showBWSim && !showSimFrames && simSteps?.success

  return (
    <div className={cn('space-y-4', className)}>
      {/* Animation Toggle */}
      {animationUrl && (
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-lapis-muted">Plan Visualization</span>
          <button
            onClick={() => setShowAnimation(!showAnimation)}
            className="px-3 py-1 text-xs rounded-lg bg-lapis-card border border-lapis-border hover:border-lapis-accent text-lapis-text transition-colors"
          >
            {showAnimation ? 'Show Step-by-Step' : 'Show Full Animation'}
          </button>
        </div>
      )}

      {/* Full Animation GIF */}
      {showAnimation && animationUrl && (
        <div className="border border-lapis-border rounded-lg overflow-hidden bg-lapis-bg">
          <img src={animationUrl} alt="Plan animation" className="w-full h-auto" />
        </div>
      )}

      {/* Step-by-step view */}
      {!showAnimation && (
        <>
          {/* Blocksworld tower simulator */}
          {showBWSim && (
            <BlocksworldSim
              problemPddl={problemPddl!}
              actions={normalizedActions}
              step={currentStep}
            />
          )}

          {/* Graphical frame viewer for IPC domains with graphical simulators */}
          {showSimFrames && (
            <div className="border border-lapis-border rounded-lg overflow-hidden bg-lapis-bg">
              <img
                src={simFrames!.frames[currentStep + 1] ?? simFrames!.frames[currentStep] ?? simFrames!.frames[0]}
                alt={`State after step ${currentStep + 1}`}
                className="w-full h-auto"
              />
            </div>
          )}

          {/* State diff viewer — supplementary when graphical frames available, primary otherwise */}
          {simSteps?.success && (showSimDiff || showSimFrames) && (
            <SimDiffViewer
              simSteps={simSteps}
              step={currentStep}
              collapsible={showSimFrames}
            />
          )}

          {/* Step image (if provided and no domain simulator or graphical frames) */}
          {!showBWSim && !showSimFrames && !showSimDiff && currentImage && (
            <div className="border border-lapis-border rounded-lg overflow-hidden bg-lapis-bg">
              <img src={currentImage} alt={`Step ${currentStep + 1}`} className="w-full h-auto" />
            </div>
          )}

          {/* Navigation Controls */}
          <div className="flex items-center gap-3">
            <button
              onClick={handlePrev}
              disabled={currentStep === 0}
              className={cn(
                'p-2 rounded-lg transition-colors',
                currentStep === 0
                  ? 'bg-lapis-border text-lapis-muted cursor-not-allowed'
                  : 'bg-lapis-card hover:bg-lapis-accent/20 text-lapis-text'
              )}
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <div className="flex-1">
              <Slider.Root
                value={[currentStep]}
                onValueChange={([value]) => setCurrentStep(value)}
                min={0}
                max={n - 1}
                step={1}
                className="relative flex items-center select-none touch-none w-full h-5"
              >
                <Slider.Track className="bg-lapis-border relative grow rounded-full h-2">
                  <Slider.Range className="absolute bg-lapis-accent rounded-full h-full" />
                </Slider.Track>
                <Slider.Thumb
                  className={cn(
                    'block w-5 h-5 bg-lapis-accent rounded-full shadow-lg',
                    'hover:bg-lapis-accent/80 focus:outline-none focus:ring-2 focus:ring-lapis-accent/50',
                    'transition-colors cursor-pointer'
                  )}
                />
              </Slider.Root>
            </div>

            <button
              onClick={handleNext}
              disabled={currentStep === n - 1}
              className={cn(
                'p-2 rounded-lg transition-colors',
                currentStep === n - 1
                  ? 'bg-lapis-border text-lapis-muted cursor-not-allowed'
                  : 'bg-lapis-card hover:bg-lapis-accent/20 text-lapis-text'
              )}
            >
              <ChevronRight className="w-4 h-4" />
            </button>

            <span className="text-sm text-lapis-muted min-w-[60px] text-right">
              {currentStep + 1} / {n}
            </span>
          </div>

          {/* Current Action Banner */}
          <div className="plan-current-action">
            <span className="text-lapis-muted text-sm">Step {currentStep + 1}</span>
            <span className="text-lapis-accent font-semibold">{name}</span>
            {params.length > 0 && (
              <span className="text-lapis-text-secondary">{params.join(' ')}</span>
            )}
          </div>

          {/* Action List */}
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {normalizedActions.map((action, i) => {
              const isActive = i === currentStep
              const isPast = i < currentStep
              const aClean = action.replace(/^\(|\)$/g, '').trim()
              const aParts = aClean.split(/\s+/)

              return (
                <div
                  key={i}
                  onClick={() => setCurrentStep(i)}
                  className={cn(
                    'plan-step cursor-pointer transition-all duration-150',
                    isActive && 'plan-step-active',
                    isPast && 'opacity-60'
                  )}
                >
                  <span
                    className={cn(
                      'w-8 text-right text-sm',
                      isActive ? 'text-lapis-accent font-semibold' : 'text-lapis-muted'
                    )}
                  >
                    {i + 1}.
                  </span>
                  <span className={cn('font-mono', isActive && 'text-lapis-accent')}>
                    ({aParts[0]}
                    {aParts.slice(1).length > 0 && <span className="text-lapis-text-secondary"> {aParts.slice(1).join(' ')}</span>})
                  </span>
                </div>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}

export default PlanTrace
