/**
 * PDDLViewer - Syntax-highlighted PDDL viewer with diff support.
 *
 * Features:
 * - Syntax highlighting for PDDL
 * - Side-by-side diff view
 * - Predicate mismatch detection
 */
import { useMemo, useState } from 'react'
import { Highlight, themes } from 'prism-react-renderer'
import { cn } from '@/lib/utils'
import { Copy, Check, AlertTriangle } from 'lucide-react'

// Custom PDDL grammar for Prism (unused but kept for future enhancements)
// const pddlGrammar = {
//   comment: /;.*/,
//   keyword: /:\w+/,
//   string: /"(?:[^"\\]|\\.)*"/,
//   builtin: /\b(?:define|domain|problem|and|or|not|when|forall|exists|imply)\b/,
//   function: /\b(?:action|durative-action|parameters|precondition|effect|condition|duration)\b/,
//   operator: /[?!]/,
//   punctuation: /[()]/,
// }

interface PDDLViewerProps {
  code: string
  title?: string
  className?: string
  showCopy?: boolean
  maxHeight?: string
}

export function PDDLViewer({
  code,
  title,
  className,
  showCopy = true,
  maxHeight = '400px',
}: PDDLViewerProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (!code) {
    return (
      <div className={cn('text-lapis-muted text-sm p-4 bg-lapis-card rounded-lg', className)}>
        No PDDL content available.
      </div>
    )
  }

  return (
    <div className={cn('relative rounded-lg overflow-hidden', className)}>
      {/* Header */}
      {(title || showCopy) && (
        <div className="flex items-center justify-between px-4 py-2 bg-lapis-card/80 border-b border-lapis-border">
          {title && <span className="text-sm font-medium text-lapis-text">{title}</span>}
          {showCopy && (
            <button
              onClick={handleCopy}
              className="p-1.5 rounded hover:bg-lapis-accent/20 transition-colors"
              title="Copy to clipboard"
            >
              {copied ? (
                <Check className="w-4 h-4 text-lapis-success" />
              ) : (
                <Copy className="w-4 h-4 text-lapis-muted" />
              )}
            </button>
          )}
        </div>
      )}

      {/* Code */}
      <div className="overflow-auto" style={{ maxHeight }}>
        <Highlight
          theme={themes.vsDark}
          code={code.trim()}
          language="lisp"
        >
          {({ className: hlClassName, style, tokens, getLineProps, getTokenProps }) => (
            <pre
              className={cn(hlClassName, 'p-4 text-xs font-mono leading-relaxed')}
              style={{ ...style, margin: 0, background: '#1e1e2e' }}
            >
              {tokens.map((line, i) => (
                <div key={i} {...getLineProps({ line })}>
                  <span className="inline-block w-8 text-right mr-4 text-slate-500 select-none">
                    {i + 1}
                  </span>
                  {line.map((token, key) => (
                    <span key={key} {...getTokenProps({ token })} />
                  ))}
                </div>
              ))}
            </pre>
          )}
        </Highlight>
      </div>
    </div>
  )
}

// --- Diff View ---

interface PDDLDiffViewProps {
  leftCode: string
  rightCode: string
  leftTitle?: string
  rightTitle?: string
  className?: string
}

export function PDDLDiffView({
  leftCode,
  rightCode,
  leftTitle = 'Generated',
  rightTitle = 'Ground Truth',
  className,
}: PDDLDiffViewProps) {
  return (
    <div className={cn('grid grid-cols-2 gap-4', className)}>
      <PDDLViewer code={leftCode} title={leftTitle} maxHeight="500px" />
      <PDDLViewer code={rightCode} title={rightTitle} maxHeight="500px" />
    </div>
  )
}

// --- Predicate Mismatch ---

interface PredicateMismatchProps {
  generatedPddl: string
  groundTruthPddl: string
  className?: string
}

/**
 * Extract predicate names from a PDDL domain string.
 */
function extractPredicates(pddl: string): Set<string> {
  if (!pddl) return new Set()

  // Find the :predicates block
  const match = pddl.match(/:predicates(.+?)(?=\s*\(:\w|\Z)/s)
  if (!match) return new Set()

  const block = match[1]
  // Extract predicate names (first token after opening paren)
  const names = block.match(/\(\s*([A-Za-z][A-Za-z0-9_-]*)/g) || []

  return new Set(
    names.map((n) => n.replace(/\(\s*/, '').toLowerCase())
  )
}

export function PredicateMismatch({
  generatedPddl,
  groundTruthPddl,
  className,
}: PredicateMismatchProps) {
  const mismatch = useMemo(() => {
    const generated = extractPredicates(generatedPddl)
    const gt = extractPredicates(groundTruthPddl)

    const onlyGenerated = [...generated].filter((p) => !gt.has(p))
    const onlyGT = [...gt].filter((p) => !generated.has(p))
    const common = [...generated].filter((p) => gt.has(p))

    return { onlyGenerated, onlyGT, common }
  }, [generatedPddl, groundTruthPddl])

  const hasMismatch = mismatch.onlyGenerated.length > 0 || mismatch.onlyGT.length > 0

  if (!hasMismatch) {
    return (
      <div className={cn('p-3 rounded-lg bg-lapis-success/10 border border-lapis-success/30', className)}>
        <div className="flex items-center gap-2 text-sm text-lapis-success">
          <Check className="w-4 h-4" />
          Predicates match GT - {mismatch.common.length} in common
        </div>
      </div>
    )
  }

  return (
    <div className={cn('p-4 rounded-lg bg-amber-500/10 border border-amber-500/30', className)}>
      <div className="flex items-center gap-2 text-sm font-medium text-amber-400 mb-3">
        <AlertTriangle className="w-4 h-4" />
        Predicate Mismatches
      </div>

      <div className="grid grid-cols-2 gap-4">
        {mismatch.onlyGenerated.length > 0 && (
          <div>
            <div className="text-xs font-medium text-lapis-muted mb-2">
              In generated, not in GT:
            </div>
            <div className="space-y-1">
              {mismatch.onlyGenerated.map((p) => (
                <div
                  key={p}
                  className="text-xs font-mono px-2 py-1 rounded bg-amber-500/20 text-amber-300"
                >
                  {p}
                </div>
              ))}
            </div>
          </div>
        )}

        {mismatch.onlyGT.length > 0 && (
          <div>
            <div className="text-xs font-medium text-lapis-muted mb-2">
              In GT, not in generated:
            </div>
            <div className="space-y-1">
              {mismatch.onlyGT.map((p) => (
                <div
                  key={p}
                  className="text-xs font-mono px-2 py-1 rounded bg-red-500/20 text-red-300"
                >
                  {p}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {mismatch.common.length > 0 && (
        <div className="mt-3 pt-3 border-t border-lapis-border">
          <div className="text-xs text-lapis-muted">
            {mismatch.common.length} predicates in common
          </div>
        </div>
      )}
    </div>
  )
}

export default PDDLViewer
