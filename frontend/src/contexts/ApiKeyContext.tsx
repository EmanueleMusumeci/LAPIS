import { createContext, useContext, useState, useRef, useEffect, type ReactNode } from 'react'
import { KeyRound, AlertOctagon, CheckCircle2 } from 'lucide-react'

interface ApiKeyContextValue {
  apiKey: string
  setApiKey: (key: string) => void
}

const ApiKeyContext = createContext<ApiKeyContextValue>({
  apiKey: '',
  setApiKey: () => {},
})

export function ApiKeyProvider({ children }: { children: ReactNode }) {
  const [apiKey, setApiKey] = useState('')
  return (
    <ApiKeyContext.Provider value={{ apiKey, setApiKey }}>
      {children}
    </ApiKeyContext.Provider>
  )
}

export function useApiKey() {
  return useContext(ApiKeyContext)
}

/**
 * Compact key-icon button that opens a popover with the API key input.
 * Shows an amber warning indicator when no key is set.
 * Used in both AgenticEditor and LiveExecution headers.
 */
export function ApiKeyDropdown({ className }: { className?: string }) {
  const { apiKey, setApiKey } = useApiKey()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  return (
    <div className={`relative ${className ?? ''}`} ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        title={apiKey ? 'API key set — click to change' : 'No API key — click to set'}
        className={`flex items-center gap-1 px-2 py-1 rounded-lg border text-xs transition-colors ${
          apiKey
            ? 'border-lapis-border text-lapis-muted hover:border-lapis-accent/40 hover:text-lapis-text'
            : 'border-amber-500/50 bg-amber-500/10 text-amber-400 hover:border-amber-500/80'
        }`}
      >
        <KeyRound className="w-3.5 h-3.5" />
        {!apiKey && <AlertOctagon className="w-3 h-3" />}
        {apiKey
          ? <span className="font-mono">{apiKey.slice(0, 8)}…</span>
          : <span>No key</span>
        }
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1.5 z-50 w-72 rounded-xl border border-lapis-border bg-lapis-card shadow-xl p-3 space-y-2">
          <label className="flex items-center gap-1.5 text-xs font-medium text-lapis-muted">
            <KeyRound className="w-3 h-3" />
            API Key
            <span className="font-normal text-lapis-text-secondary">(Anthropic or OpenAI)</span>
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk-ant-… or sk-…"
            autoComplete="off"
            autoFocus
            className="w-full px-3 py-2 rounded-lg bg-lapis-bg border border-lapis-border text-lapis-text text-sm font-mono placeholder:text-lapis-text-secondary focus:outline-none focus:border-lapis-accent"
          />
          {apiKey ? (
            <p className="text-xs text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" />
              Key set ({apiKey.startsWith('sk-ant') ? 'Anthropic' : 'OpenAI'})
            </p>
          ) : (
            <p className="text-xs text-amber-400 flex items-center gap-1">
              <AlertOctagon className="w-3 h-3" />
              Leave blank to use the server default key
            </p>
          )}
        </div>
      )}
    </div>
  )
}

/**
 * @deprecated Use ApiKeyDropdown instead.
 */
export function ApiKeyInput({ className }: { className?: string }) {
  return <ApiKeyDropdown className={className} />
}
