/**
 * usePipeline hook - WebSocket-based pipeline execution with real-time updates.
 */
import { useState, useCallback, useRef, useEffect } from 'react'
import type { PipelineConfig, StageResult, RunResult, WSMessage } from '@/types'
import { createPipelineWebSocket } from '@/lib/api'

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error'

export interface UsePipelineReturn {
  // State
  connectionStatus: ConnectionStatus
  isRunning: boolean
  runId: string | null
  stages: StageResult[]
  result: RunResult | null
  error: string | null

  // Actions
  connect: () => void
  disconnect: () => void
  runPipeline: (config: PipelineConfig) => void
  cancelPipeline: () => void
  reset: () => void
}

export function usePipeline(): UsePipelineReturn {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected')
  const [isRunning, setIsRunning] = useState(false)
  const [runId, setRunId] = useState<string | null>(null)
  const [stages, setStages] = useState<StageResult[]>([])
  const [result, setResult] = useState<RunResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const isMountedRef = useRef(true)

  const connect = useCallback(() => {
    // Don't create new connection if one is already open or connecting
    if (wsRef.current) {
      const state = wsRef.current.readyState
      if (state === WebSocket.OPEN || state === WebSocket.CONNECTING) {
        console.log('[LAPIS] WebSocket already open/connecting, skipping')
        return
      }
    }

    console.log('[LAPIS] Creating new WebSocket connection')
    setConnectionStatus('connecting')
    setError(null)

    try {
      const ws = createPipelineWebSocket()
      wsRef.current = ws

      ws.onopen = () => {
        console.log('[LAPIS] WebSocket onopen')
        if (isMountedRef.current) {
          setConnectionStatus('connected')
        }
      }

      ws.onclose = (event) => {
        console.log('[LAPIS] WebSocket onclose', event.code, event.reason)
        if (isMountedRef.current) {
          setConnectionStatus('disconnected')
        }
        // Only nullify if this is the current websocket
        if (wsRef.current === ws) {
          wsRef.current = null
        }
      }

      ws.onerror = (event) => {
        console.error('[LAPIS] WebSocket onerror', event)
        if (isMountedRef.current) {
          setConnectionStatus('error')
          setError('WebSocket connection failed')
        }
      }

      ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data)
          handleMessage(message)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }
    } catch (e) {
      setConnectionStatus('error')
      setError(`Failed to connect: ${e}`)
    }
  }, [])

  const handleMessage = useCallback((message: WSMessage) => {
    switch (message.type) {
      case 'connected':
        setRunId(message.run_id || null)
        break

      case 'run_started':
        setRunId(message.run_id || null)
        setIsRunning(true)
        setStages([])
        setResult(null)
        setError(null)
        break

      case 'stage_update': {
        const stageData = message.data as StageResult
        setStages((prev) => {
          const idx = prev.findIndex((s) => s.name === stageData.name)
          if (idx >= 0) {
            const updated = [...prev]
            updated[idx] = stageData
            return updated
          }
          return [...prev, stageData]
        })
        break
      }

      case 'complete':
        setResult(message.data as RunResult)
        setIsRunning(false)
        break

      case 'error':
        setError(message.message || 'Unknown error')
        setIsRunning(false)
        break
    }
  }, [])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setConnectionStatus('disconnected')
  }, [])

  const runPipeline = useCallback((config: PipelineConfig) => {
    const ws = wsRef.current
    const readyState = ws?.readyState
    const readyStateNames = ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED']

    console.log('[LAPIS] runPipeline called', {
      hasWebSocket: !!ws,
      readyState,
      readyStateName: readyState !== undefined ? readyStateNames[readyState] : 'undefined',
      isRunning,
    })

    if (!ws || readyState !== WebSocket.OPEN) {
      console.error('[LAPIS] WebSocket not connected, readyState:', readyState)
      setError('Not connected to server. Please wait for connection or refresh the page.')

      // Try to reconnect
      if (!ws || readyState === WebSocket.CLOSED) {
        console.log('[LAPIS] Attempting to reconnect...')
        connect()
      }
      return
    }

    if (isRunning) {
      console.error('[LAPIS] Pipeline already running')
      setError('Pipeline already running')
      return
    }

    setError(null) // Clear any previous error
    const message = JSON.stringify({
      type: 'run',
      config,
    })
    console.log('[LAPIS] Sending WebSocket message:', message)
    ws.send(message)
  }, [isRunning, connect])

  const cancelPipeline = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return

    wsRef.current.send(JSON.stringify({
      type: 'cancel',
    }))
  }, [])

  const reset = useCallback(() => {
    setStages([])
    setResult(null)
    setError(null)
    setRunId(null)
    setIsRunning(false)
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    isMountedRef.current = true
    return () => {
      isMountedRef.current = false
      // Don't disconnect on cleanup in dev mode - let the connection persist
      // This avoids issues with React Strict Mode double-mounting
    }
  }, [])

  // Auto-connect on mount
  useEffect(() => {
    // Small delay to let React Strict Mode settle
    const timer = setTimeout(() => {
      if (isMountedRef.current && (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED)) {
        connect()
      }
    }, 100)
    return () => clearTimeout(timer)
  }, [connect])

  return {
    connectionStatus,
    isRunning,
    runId,
    stages,
    result,
    error,
    connect,
    disconnect,
    runPipeline,
    cancelPipeline,
    reset,
  }
}
