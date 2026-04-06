import { useCallback, useEffect, useRef, useState } from 'react'
import { createPipelineWebSocket } from '@/lib/api'
import type {
  A2UIBlueprint,
  AgentMessageData,
  EditorUpdateData,
  ExtendedWSMessage,
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
  uiBlueprint: A2UIBlueprint | null
  isLoading: boolean
  error: string | null
}

const DEFAULT_DOMAIN = `(define (domain demo)\n  (:requirements :strips :typing)\n  (:types block)\n  (:predicates (on ?x - block ?y - block) (clear ?x - block))\n  (:action stack\n    :parameters (?x - block ?y - block)\n    :precondition (and (clear ?x) (clear ?y))\n    :effect (and (on ?x ?y) (not (clear ?y)))))`

const DEFAULT_PROBLEM = `(define (problem demo-problem)\n  (:domain demo)\n  (:objects a b - block)\n  (:init (clear a) (clear b))\n  (:goal (on a b)))`

export function useAgenticEditor() {
  const [state, setState] = useState<AgenticEditorState>({
    connected: false,
    domainPddl: DEFAULT_DOMAIN,
    problemPddl: DEFAULT_PROBLEM,
    userInput: '',
    chat: [],
    verification: null,
    uiBlueprint: null,
    isLoading: false,
    error: null,
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
    setState((prev) => ({ ...prev, isLoading: true, error: null }))
    send({
      type: 'VERIFY_REQUEST',
      domain: state.domainPddl,
      problem: state.problemPddl,
    })
  }, [send, state.domainPddl, state.problemPddl])

  const sendUserMessage = useCallback((text: string) => {
    const trimmed = text.trim()
    if (!trimmed) return

    setState((prev) => ({
      ...prev,
      chat: [...prev.chat, { role: 'user', text: trimmed, at: Date.now() }],
      userInput: '',
      isLoading: true,
      error: null,
    }))

    send({
      type: 'USER_MESSAGE',
      text: trimmed,
      domain: state.domainPddl,
      problem: state.problemPddl,
    })
  }, [send, state.domainPddl, state.problemPddl])

  const syncFromText = useCallback((domain: string, problem: string) => {
    setState((prev) => ({ ...prev, domainPddl: domain, problemPddl: problem }))

    if (verifyDebounceRef.current) {
      clearTimeout(verifyDebounceRef.current)
    }
    verifyDebounceRef.current = window.setTimeout(() => {
      send({ type: 'PDDL_UPDATE', domain, problem, source: 'text' })
    }, 500)
  }, [send])

  const syncFromGraphical = useCallback((domain: string, problem: string) => {
    setState((prev) => ({ ...prev, domainPddl: domain, problemPddl: problem }))
    send({ type: 'PDDL_UPDATE', domain, problem, source: 'graphical' })
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
          }))
          return
        }

        if (message.type === 'VERIFY_RESULTS') {
          const payload = (message.data || null) as VerificationPayload | null
          setState((prev) => ({ ...prev, verification: payload, isLoading: false }))
          return
        }

        if (message.type === 'VIZ_BLUEPRINT') {
          const payload = message.data as { blueprint: A2UIBlueprint }
          setState((prev) => ({ ...prev, uiBlueprint: payload.blueprint }))
          return
        }

        if (message.type === 'error') {
          setState((prev) => ({ ...prev, isLoading: false, error: message.message || 'Unknown error' }))
        }
      } catch {
        setState((prev) => ({ ...prev, isLoading: false, error: 'Invalid server response' }))
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
  }
}
