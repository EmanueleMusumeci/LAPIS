/**
 * ConfigPanel - Configuration options for pipeline execution.
 */
import { ChevronDown, Cpu, Timer, RefreshCw, Shield, Layers, Database, Zap, FlaskConical } from 'lucide-react'
import * as Select from '@radix-ui/react-select'
import * as Slider from '@radix-ui/react-slider'
import { cn } from '@/lib/utils'
import type { PipelineMethod } from '@/types'

const MODELS: Record<string, string> = {
  'claude-sonnet-4-6': 'Claude Sonnet 4.6',
  'claude-3-5-sonnet-20241022': 'Claude 3.5 Sonnet',
  'gpt-4o': 'GPT-4o',
  'gpt-4o-mini': 'GPT-4o mini',
}

const PLANNERS = ['pyperplan', 'up_fd', 'fd']

interface ConfigPanelProps {
  modelId: string
  onModelChange: (model: string) => void
  plannerName: string
  onPlannerChange: (planner: string) => void
  maxRefinements: number
  onRefinementsChange: (value: number) => void
  plannerTimeout: number
  onTimeoutChange: (value: number) => void
  skipAdequacy: boolean
  onSkipAdequacyChange: (value: boolean) => void
  semanticChecks: boolean
  onSemanticChecksChange: (value: boolean) => void
  method: PipelineMethod
  onMethodChange: (method: PipelineMethod) => void
  className?: string
}

export function ConfigPanel({
  modelId,
  onModelChange,
  plannerName,
  onPlannerChange,
  maxRefinements,
  onRefinementsChange,
  plannerTimeout,
  onTimeoutChange,
  skipAdequacy,
  onSkipAdequacyChange,
  semanticChecks,
  onSemanticChecksChange,
  method,
  onMethodChange,
  className,
}: ConfigPanelProps) {
  return (
    <div className={cn('space-y-4', className)}>
      {/* Method Selection — visual cards */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-lapis-text">Pipeline Method</label>
        <div className="grid grid-cols-1 gap-1.5">
          {(
            [
              {
                id: 'lapis',
                icon: <Layers className="w-4 h-4" />,
                label: 'LAPI(S)²',
                sub: 'Full: domain gen → adequacy → problem gen → refine',
                accent: 'lapis',
              },
              {
                id: 'lapis_noadq',
                icon: <Layers className="w-4 h-4" />,
                label: 'LAPI(S)² (no adq.)',
                sub: 'Skips the domain adequacy check',
                accent: 'lapis',
              },
              {
                id: 'gt_lapis',
                icon: <Database className="w-4 h-4" />,
                label: 'GT-LAPI(S)²',
                sub: 'Ground-truth domain + LAPIS² problem gen & refinement',
                accent: 'violet',
              },
              {
                id: 'sim_val',
                icon: <FlaskConical className="w-4 h-4" />,
                label: 'Sim-LAPI(S)² VAL',
                sub: 'LAPI(S)² + UP sequential simulator validates plans',
                accent: 'orange',
              },
              {
                id: 'llmpp',
                icon: <Zap className="w-4 h-4" />,
                label: 'LLM+P',
                sub: 'GT domain injected, generate problem, 0 refinements',
                accent: 'slate',
              },
            ] as Array<{ id: PipelineMethod; icon: React.ReactNode; label: string; sub: string; accent: string }>
          ).map((m) => {
            const isSelected = method === m.id
            const accentMap: Record<string, string> = {
              lapis: 'border-lapis-accent/60 bg-lapis-accent/10 text-lapis-accent',
              violet: 'border-violet-500/60 bg-violet-500/10 text-violet-400',
              orange: 'border-orange-500/60 bg-orange-500/10 text-orange-400',
              slate: 'border-slate-500/60 bg-slate-500/10 text-slate-400',
            }
            return (
              <button
                key={m.id}
                type="button"
                onClick={() => onMethodChange(m.id)}
                className={cn(
                  'w-full text-left px-3 py-2.5 rounded-lg border transition-all text-sm',
                  isSelected
                    ? accentMap[m.accent] || accentMap['lapis']
                    : 'border-lapis-border bg-lapis-bg/60 text-lapis-text-secondary hover:border-lapis-accent/30 hover:text-lapis-text'
                )}
              >
                <div className="flex items-center gap-2">
                  <span className={isSelected ? '' : 'opacity-50'}>{m.icon}</span>
                  <span className={cn('font-semibold', isSelected ? '' : 'text-lapis-text')}>{m.label}</span>
                </div>
                <p className="mt-0.5 pl-6 text-xs opacity-70">{m.sub}</p>
              </button>
            )
          })}
        </div>
      </div>

      {/* Model Selection */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-lapis-text flex items-center gap-2">
          <Cpu className="w-4 h-4 text-lapis-accent" />
          LLM Model
        </label>
        <Select.Root value={modelId} onValueChange={onModelChange}>
          <Select.Trigger
            className={cn(
              'flex items-center justify-between w-full px-3 py-2 rounded-lg',
              'bg-lapis-card border border-lapis-border',
              'text-sm text-lapis-text',
              'hover:border-lapis-accent/50 focus:outline-none focus:ring-2 focus:ring-lapis-accent/30'
            )}
          >
            <Select.Value />
            <Select.Icon>
              <ChevronDown className="w-4 h-4 text-lapis-muted" />
            </Select.Icon>
          </Select.Trigger>

          <Select.Portal>
            <Select.Content
              className="overflow-hidden rounded-lg bg-lapis-card border border-lapis-border shadow-xl z-50"
              position="popper"
              sideOffset={4}
            >
              <Select.Viewport className="p-1">
                {Object.entries(MODELS).map(([id, name]) => (
                  <Select.Item
                    key={id}
                    value={id}
                    className={cn(
                      'px-3 py-2 rounded-md text-sm cursor-pointer',
                      'text-lapis-text',
                      'hover:bg-lapis-accent/20 focus:bg-lapis-accent/20 focus:outline-none',
                      'data-[highlighted]:bg-lapis-accent/20'
                    )}
                  >
                    <Select.ItemText>{name}</Select.ItemText>
                  </Select.Item>
                ))}
              </Select.Viewport>
            </Select.Content>
          </Select.Portal>
        </Select.Root>
      </div>

      {/* Planner Selection */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-lapis-text flex items-center gap-2">
          <Shield className="w-4 h-4 text-lapis-accent" />
          Planner Backend
        </label>
        <Select.Root value={plannerName} onValueChange={onPlannerChange}>
          <Select.Trigger
            className={cn(
              'flex items-center justify-between w-full px-3 py-2 rounded-lg',
              'bg-lapis-card border border-lapis-border',
              'text-sm text-lapis-text',
              'hover:border-lapis-accent/50 focus:outline-none focus:ring-2 focus:ring-lapis-accent/30'
            )}
          >
            <Select.Value />
            <Select.Icon>
              <ChevronDown className="w-4 h-4 text-lapis-muted" />
            </Select.Icon>
          </Select.Trigger>

          <Select.Portal>
            <Select.Content
              className="overflow-hidden rounded-lg bg-lapis-card border border-lapis-border shadow-xl z-50"
              position="popper"
              sideOffset={4}
            >
              <Select.Viewport className="p-1">
                {PLANNERS.map((planner) => (
                  <Select.Item
                    key={planner}
                    value={planner}
                    className={cn(
                      'px-3 py-2 rounded-md text-sm cursor-pointer',
                      'text-lapis-text',
                      'hover:bg-lapis-accent/20 focus:bg-lapis-accent/20 focus:outline-none',
                      'data-[highlighted]:bg-lapis-accent/20'
                    )}
                  >
                    <Select.ItemText>{planner}</Select.ItemText>
                  </Select.Item>
                ))}
              </Select.Viewport>
            </Select.Content>
          </Select.Portal>
        </Select.Root>
      </div>

      {/* Max Refinements Slider */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-lapis-text flex items-center justify-between">
          <span className="flex items-center gap-2">
            <RefreshCw className="w-4 h-4 text-lapis-accent" />
            Max Refinements
          </span>
          <span className="text-lapis-accent">{maxRefinements}</span>
        </label>
        <Slider.Root
          value={[maxRefinements]}
          onValueChange={([value]) => onRefinementsChange(value)}
          min={0}
          max={5}
          step={1}
          className="relative flex items-center select-none touch-none w-full h-5"
        >
          <Slider.Track className="bg-lapis-border relative grow rounded-full h-1.5">
            <Slider.Range className="absolute bg-lapis-accent rounded-full h-full" />
          </Slider.Track>
          <Slider.Thumb
            className={cn(
              'block w-4 h-4 bg-lapis-accent rounded-full',
              'hover:bg-lapis-accent/80 focus:outline-none focus:ring-2 focus:ring-lapis-accent/50',
              'transition-colors cursor-pointer'
            )}
          />
        </Slider.Root>
      </div>

      {/* Planner Timeout Slider */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-lapis-text flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Timer className="w-4 h-4 text-lapis-accent" />
            Planner Timeout
          </span>
          <span className="text-lapis-accent">{plannerTimeout}s</span>
        </label>
        <Slider.Root
          value={[plannerTimeout]}
          onValueChange={([value]) => onTimeoutChange(value)}
          min={30}
          max={300}
          step={30}
          className="relative flex items-center select-none touch-none w-full h-5"
        >
          <Slider.Track className="bg-lapis-border relative grow rounded-full h-1.5">
            <Slider.Range className="absolute bg-lapis-accent rounded-full h-full" />
          </Slider.Track>
          <Slider.Thumb
            className={cn(
              'block w-4 h-4 bg-lapis-accent rounded-full',
              'hover:bg-lapis-accent/80 focus:outline-none focus:ring-2 focus:ring-lapis-accent/50',
              'transition-colors cursor-pointer'
            )}
          />
        </Slider.Root>
      </div>

      {/* Adequacy Check Toggle (methods that use domain gen) */}
      {(method === 'lapis' || method === 'sim_val') && (
        <div className="flex items-center justify-between">
          <div>
            <label className="text-sm font-medium text-lapis-text">Domain Adequacy Check</label>
            <p className="text-xs text-lapis-muted">Amend domain to cover problem predicates</p>
          </div>
          <button
            onClick={() => onSkipAdequacyChange(!skipAdequacy)}
            className={cn(
              'relative w-11 h-6 rounded-full transition-colors flex-shrink-0',
              skipAdequacy ? 'bg-lapis-border' : 'bg-lapis-accent'
            )}
          >
            <span
              className={cn(
                'absolute top-1 w-4 h-4 rounded-full bg-white transition-transform',
                skipAdequacy ? 'left-1' : 'left-6'
              )}
            />
          </button>
        </div>
      )}

      {/* Semantic Checks Toggle */}
      {(method === 'lapis' || method === 'lapis_noadq' || method === 'gt_lapis' || method === 'sim_val') && (
        <div className="flex items-center justify-between">
          <div>
            <label className="text-sm font-medium text-lapis-text">Semantic Validity Checks</label>
            <p className="text-xs text-lapis-muted">Predicate coverage, action reachability</p>
          </div>
          <button
            onClick={() => onSemanticChecksChange(!semanticChecks)}
            className={cn(
              'relative w-11 h-6 rounded-full transition-colors flex-shrink-0',
              semanticChecks ? 'bg-lapis-accent' : 'bg-lapis-border'
            )}
          >
            <span
              className={cn(
                'absolute top-1 w-4 h-4 rounded-full bg-white transition-transform',
                semanticChecks ? 'left-6' : 'left-1'
              )}
            />
          </button>
        </div>
      )}
    </div>
  )
}

export default ConfigPanel
