/**
 * PresetSelector - Domain and problem preset selection.
 */
import { useMemo } from 'react'
import { ChevronDown, FileText } from 'lucide-react'
import * as Select from '@radix-ui/react-select'
import { cn } from '@/lib/utils'
import type { Preset } from '@/types'

interface PresetSelectorProps {
  presets: Preset[]
  selectedPreset: Preset | null
  onPresetChange: (preset: Preset | null) => void
  className?: string
}

export function PresetSelector({
  presets,
  selectedPreset,
  onPresetChange,
  className,
}: PresetSelectorProps) {
  // Group presets by domain
  const groupedPresets = useMemo(() => {
    const groups = new Map<string, Preset[]>()
    for (const preset of presets) {
      const domain = preset.domain
      if (!groups.has(domain)) {
        groups.set(domain, [])
      }
      groups.get(domain)!.push(preset)
    }
    return groups
  }, [presets])

  const domains = Array.from(groupedPresets.keys()).sort()

  return (
    <div className={cn('space-y-2', className)}>
      <label className="text-sm font-medium text-lapis-text">Preset Problem</label>

      <Select.Root
        value={selectedPreset?.id || ''}
        onValueChange={(id) => {
          if (id === 'custom') {
            onPresetChange(null)
          } else {
            const preset = presets.find((p) => p.id === id)
            onPresetChange(preset || null)
          }
        }}
      >
        <Select.Trigger
          className={cn(
            'flex items-center justify-between w-full px-3 py-2 rounded-lg',
            'bg-lapis-card border border-lapis-border',
            'text-sm text-lapis-text',
            'hover:border-lapis-accent/50 focus:outline-none focus:ring-2 focus:ring-lapis-accent/30',
            'transition-colors'
          )}
        >
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-lapis-accent" />
            <Select.Value placeholder="Select a preset..." />
          </div>
          <Select.Icon>
            <ChevronDown className="w-4 h-4 text-lapis-muted" />
          </Select.Icon>
        </Select.Trigger>

        <Select.Portal>
          <Select.Content
            className={cn(
              'overflow-hidden rounded-lg',
              'bg-lapis-card border border-lapis-border shadow-xl',
              'z-50'
            )}
            position="popper"
            sideOffset={4}
          >
            <Select.Viewport className="p-1 max-h-80">
              {/* Custom option */}
              <Select.Item
                value="custom"
                className={cn(
                  'flex items-center gap-2 px-3 py-2 rounded-md text-sm',
                  'text-lapis-text cursor-pointer',
                  'hover:bg-lapis-accent/20 focus:bg-lapis-accent/20 focus:outline-none',
                  'data-[highlighted]:bg-lapis-accent/20'
                )}
              >
                <Select.ItemText>Custom (enter your own)</Select.ItemText>
              </Select.Item>

              <Select.Separator className="h-px bg-lapis-border my-1" />

              {/* Grouped presets */}
              {domains.map((domain) => (
                <Select.Group key={domain}>
                  <Select.Label className="px-3 py-1.5 text-xs font-semibold text-lapis-muted uppercase tracking-wider">
                    {domain}
                  </Select.Label>

                  {groupedPresets.get(domain)!.map((preset) => (
                    <Select.Item
                      key={preset.id}
                      value={preset.id}
                      className={cn(
                        'flex items-center gap-2 px-3 py-2 rounded-md text-sm',
                        'text-lapis-text cursor-pointer',
                        'hover:bg-lapis-accent/20 focus:bg-lapis-accent/20 focus:outline-none',
                        'data-[highlighted]:bg-lapis-accent/20'
                      )}
                    >
                      <Select.ItemText>{preset.label}</Select.ItemText>
                    </Select.Item>
                  ))}
                </Select.Group>
              ))}
            </Select.Viewport>
          </Select.Content>
        </Select.Portal>
      </Select.Root>
    </div>
  )
}

export default PresetSelector
