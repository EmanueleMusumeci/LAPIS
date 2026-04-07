import { useMemo } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { oneDark } from '@codemirror/theme-one-dark'
import { linter, type Diagnostic } from '@codemirror/lint'

export interface PDDLIssue {
  line: number
  message: string
  severity: 'error' | 'warning'
}

interface PDDLEditorProps {
  title: string
  value: string
  onChange: (nextValue: string) => void
  issues?: PDDLIssue[]
}

function lineToOffset(text: string, line: number): number {
  const lines = text.split('\n')
  let offset = 0
  for (let idx = 0; idx < Math.max(0, line - 1) && idx < lines.length; idx += 1) {
    offset += lines[idx].length + 1
  }
  return Math.min(offset, text.length)
}

export default function PDDLEditor({ title, value, onChange, issues = [] }: PDDLEditorProps) {
  const diagnostics = useMemo<Diagnostic[]>(() => {
    return issues.map((issue) => {
      const from = lineToOffset(value, issue.line)
      const to = Math.min(value.length, from + Math.max(1, value.split('\n')[issue.line - 1]?.length || 1))
      return {
        from,
        to,
        severity: issue.severity,
        message: issue.message,
      }
    })
  }, [issues, value])

  const lintExtension = useMemo(() => linter(() => diagnostics), [diagnostics])

  return (
    <div className="rounded-xl border border-lapis-border bg-lapis-card p-3 space-y-2">
      <p className="text-xs uppercase tracking-wide text-lapis-text-secondary">{title}</p>
      <CodeMirror
        value={value}
        height="288px"
        theme={oneDark}
        basicSetup={{
          lineNumbers: true,
          foldGutter: true,
          autocompletion: false,
        }}
        extensions={[lintExtension]}
        onChange={(nextValue) => onChange(nextValue)}
      />
    </div>
  )
}
