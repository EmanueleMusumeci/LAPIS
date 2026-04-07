/**
 * usePresets hook - Load and manage presets from the API.
 */
import { useQuery } from '@tanstack/react-query'
import { getPresets, getModels } from '@/lib/api'
import type { PresetList, ModelInfo } from '@/types'

export function usePresets() {
  return useQuery<PresetList>({
    queryKey: ['presets'],
    queryFn: getPresets,
  })
}

export function useModels() {
  return useQuery<ModelInfo>({
    queryKey: ['models'],
    queryFn: getModels,
  })
}
