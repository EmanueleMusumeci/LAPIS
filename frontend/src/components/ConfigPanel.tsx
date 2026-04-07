/**
 * ConfigPanel - Configuration options for pipeline execution.
 */
import { ChevronDown, Cpu, Timer, RefreshCw, Shield } from 'lucide-react'
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
  method,
  onMethodChange,
  className,
}: ConfigPanelProps) {
  return (
    <div className={cn('space-y-4', className)}>
      {/* Method Toggle */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-lapis-text">Pipeline Method</label>
        <div className="flex gap-2">
          <button
            onClick={() => onMethodChange('lapis')}
            className={cn(
              'flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              method === 'lapis'
                ? 'bg-lapis-accent text-lapis-bg'
                : 'bg-lapis-card border border-lapis-border text-lapis-text-secondary hover:border-lapis-accent/50'
            )}
          >
            LAPIS
          </button>
          <button
            onClick={() => onMethodChange('llmpp')}
            className={cn(
              'flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              method === 'llmpp'
                ? 'bg-violet-500 text-white'
                : 'bg-lapis-card border border-lapis-border text-lapis-text-secondary hover:border-violet-500/50'
            )}
          >
            LLM+P
          </button>
        </div>
        <p className="text-xs text-lapis-muted">
          {method === 'lapis'
            ? 'Full pipeline with domain generation and adequacy checks'
            : 'Use ground-truth domain, skip adequacy checks'}
        </p>
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

      {/* Adequacy Check Toggle (LAPIS only) */}
      {method === 'lapis' && (
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-lapis-text">
            Enable Adequacy Checks
          </label>
          <button
            onClick={() => onSkipAdequacyChange(!skipAdequacy)}
            className={cn(
              'relative w-11 h-6 rounded-full transition-colors',
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
    </div>
  )
}

export default ConfigPanel
