import { useCallback, useEffect, useRef, useState } from 'react'
import { createPipelineWebSocket, getPresetPddl } from '@/lib/api'
import { useApiKey } from '@/contexts/ApiKeyContext'
import type {
  AgentMessageData,
  EditorUpdateData,
  ExtendedWSMessage,
  Preset,
  VerificationPayload,
} from '@/types'

export interface ChatEntry {
  role: 'user' | 'agent'
  text: string
  at: number
}

export interface AgenticEditorState {
  connected: boolean
  domainPddl: string
  problemPddl: string
  userInput: string
  chat: ChatEntry[]
  verification: VerificationPayload | null
  isLoading: boolean
  agentAction: string
  error: string | null
  selectedPreset: Preset | null
}

const DEFAULT_DOMAIN = `(define (domain demo)\n  (:requirements :strips :typing)\n  (:types block)\n  (:predicates (on ?x - block ?y - block) (clear ?x - block))\n  (:action stack\n    :parameters (?x - block ?y - block)\n    :precondition (and (clear ?x) (clear ?y))\n    :effect (and (on ?x ?y) (not (clear ?y)))))`

const DEFAULT_PROBLEM = `(define (problem demo-problem)\n  (:domain demo)\n  (:objects a b - block)\n  (:init (clear a) (clear b))\n  (:goal (on a b)))`

export function useAgenticEditor() {
  const { apiKey } = useApiKey()
  const [state, setState] = useState<AgenticEditorState>({
    connected: false,
    domainPddl: DEFAULT_DOMAIN,
    problemPddl: DEFAULT_PROBLEM,
    userInput: '',
    chat: [],
    verification: null,
    isLoading: false,
    agentAction: '',
    error: null,
    selectedPreset: null,
  })

  const wsRef = useRef<WebSocket | null>(null)
  const verifyDebounceRef = useRef<number | null>(null)

  const send = useCallback((payload: Record<string, unknown>) => {
    const ws = wsRef.current
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      setState((prev) => ({ ...prev, error: 'Editor socket is not connected' }))
      return false
    }
    ws.send(JSON.stringify(payload))
    return true
  }, [])

  const runVerification = useCallback(() => {
    setState((prev) => ({ ...prev, isLoading: true, agentAction: 'Verifying PDDL...', error: null }))
    send({
      type: 'VERIFY_REQUEST',
      domain: state.domainPddl,
      problem: state.problemPddl,
    })
  }, [send, state.domainPddl, state.problemPddl])

  const sendUserMessage = useCallback((text: string) => {
    const trimmed = text.trim()
    if (!trimmed) return

    if (!apiKey) {
      setState((prev) => ({ ...prev, error: 'Please enter an API key (Anthropic or OpenAI) before sending messages.' }))
      return
    }

    setState((prev) => ({
      ...prev,
      chat: [...prev.chat, { role: 'user', text: trimmed, at: Date.now() }],
      userInput: '',
      isLoading: true,
      agentAction: 'Agent is thinking...',
      error: null,
    }))

    send({
      type: 'USER_MESSAGE',
      text: trimmed,
      domain: state.domainPddl,
      problem: state.problemPddl,
      api_key: apiKey,
    })
  }, [send, state.domainPddl, state.problemPddl, apiKey])

  const syncFromText = useCallback((domain: string, problem: string) => {
    // Any manual text edit clears the preset selection → Custom
    setState((prev) => ({ ...prev, domainPddl: domain, problemPddl: problem, selectedPreset: null }))

    if (verifyDebounceRef.current) {
      clearTimeout(verifyDebounceRef.current)
    }
    verifyDebounceRef.current = window.setTimeout(() => {
      send({ type: 'PDDL_UPDATE', domain, problem, source: 'text' })
    }, 500)
  }, [send])

  const syncFromGraphical = useCallback((domain: string, problem: string) => {
    setState((prev) => ({ ...prev, domainPddl: domain, problemPddl: problem, selectedPreset: null }))
    send({ type: 'PDDL_UPDATE', domain, problem, source: 'graphical' })
  }, [send])

  const loadPreset = useCallback(async (preset: Preset | null) => {
    if (!preset) {
      setState((prev) => ({ ...prev, selectedPreset: null }))
      return
    }

    setState((prev) => ({ ...prev, isLoading: true, agentAction: `Loading ${preset.label}...`, error: null }))
    try {
      const pddl = await getPresetPddl(preset.domain, preset.problem_id)
      setState((prev) => ({
        ...prev,
        selectedPreset: preset,
        domainPddl: pddl.domain_pddl,
        problemPddl: pddl.problem_pddl,
        isLoading: false,
        agentAction: '',
        chat: [],
      }))
      send({
        type: 'INIT_SESSION',
        domain_pddl: pddl.domain_pddl,
        problem_pddl: pddl.problem_pddl,
      })
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        agentAction: '',
        error: `Failed to load preset: ${err instanceof Error ? err.message : String(err)}`,
      }))
    }
  }, [send])

  useEffect(() => {
    const ws = createPipelineWebSocket()
    wsRef.current = ws

    ws.onopen = () => {
      setState((prev) => ({ ...prev, connected: true, error: null }))
      ws.send(JSON.stringify({ type: 'INIT_SESSION' }))
    }

    ws.onclose = () => {
      setState((prev) => ({ ...prev, connected: false }))
    }

    ws.onerror = () => {
      setState((prev) => ({ ...prev, connected: false, error: 'WebSocket error' }))
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as ExtendedWSMessage

        if (message.type === 'AGENT_MESSAGE') {
          const payload = (message.data || {}) as AgentMessageData
          setState((prev) => ({
            ...prev,
            chat: [...prev.chat, { role: 'agent', text: payload.response || '', at: Date.now() }],
            domainPddl: payload.domain || prev.domainPddl,
            problemPddl: payload.problem || prev.problemPddl,
            verification: payload.verification || prev.verification,
            isLoading: false,
            agentAction: '',
          }))
          return
        }

        if (message.type === 'UPDATE') {
          const payload = (message.data || null) as EditorUpdateData | null
          if (!payload) return
          setState((prev) => ({
            ...prev,
            domainPddl: payload.domain || prev.domainPddl,
            problemPddl: payload.problem || prev.problemPddl,
            verification: payload.verification || prev.verification,
            isLoading: false,
            agentAction: '',
          }))
          return
        }

        if (message.type === 'VERIFY_RESULTS') {
          const payload = (message.data || null) as VerificationPayload | null
          setState((prev) => ({ ...prev, verification: payload, isLoading: false, agentAction: '' }))
          return
        }

        if (message.type === 'error') {
          setState((prev) => ({ ...prev, isLoading: false, agentAction: '', error: message.message || 'Unknown error' }))
        }
      } catch {
        setState((prev) => ({ ...prev, isLoading: false, agentAction: '', error: 'Invalid server response' }))
      }
    }

    return () => {
      if (verifyDebounceRef.current) {
        clearTimeout(verifyDebounceRef.current)
      }
      ws.close()
      wsRef.current = null
    }
  }, [])

  return {
    state,
    setUserInput: (value: string) => setState((prev) => ({ ...prev, userInput: value })),
    sendUserMessage,
    syncFromText,
    syncFromGraphical,
    runVerification,
    loadPreset,
  }
}
