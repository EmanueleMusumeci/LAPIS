import { createContext, useContext, useState, type ReactNode } from 'react'
import { KeyRound } from 'lucide-react'

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
 * Inline API key input widget — renders a masked password field with a key
 * icon. Both LiveExecution and AgenticEditor embed this component; they share
 * the same context value so changes on one page are reflected on the other.
 */
export function ApiKeyInput({ className }: { className?: string }) {
  const { apiKey, setApiKey } = useApiKey()

  return (
    <div className={`space-y-1 ${className ?? ''}`}>
      <label className="flex items-center gap-1 text-xs font-medium text-lapis-muted">
        <KeyRound className="w-3 h-3" />
        API Key
        <span className="text-lapis-text-secondary font-normal">(Anthropic or OpenAI)</span>
      </label>
      <input
        type="password"
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
        placeholder="sk-ant-… or sk-…"
        autoComplete="off"
        className="w-full px-3 py-2 rounded-lg bg-lapis-bg border border-lapis-border text-lapis-text text-sm font-mono placeholder:text-lapis-text-secondary focus:outline-none focus:border-lapis-accent"
      />
      {apiKey && (
        <p className="text-xs text-emerald-400">
          Key set ({apiKey.startsWith('sk-ant') ? 'Anthropic' : 'OpenAI'})
        </p>
      )}
    </div>
  )
}
