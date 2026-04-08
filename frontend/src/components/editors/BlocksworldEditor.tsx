import { useMemo, useState } from 'react'

interface BlocksworldEditorProps {
  problemPddl: string
  onChange: (updatedProblemPddl: string) => void
  readOnly?: boolean
}

interface ParsedState {
  blocks: string[]
  onRelations: Array<{ top: string; bottom: string }>
  onTable: string[]
}

function parseBlocksworld(problemPddl: string): ParsedState {
  const blocksMatch = problemPddl.match(/\(:objects([\s\S]*?)\)/i)
  const objectSection = blocksMatch ? blocksMatch[1] : ''
  const blockTokens = objectSection.match(/[a-zA-Z0-9_-]+/g) || []
  const blocks = blockTokens.filter((token) => !['block', '-', 'objects'].includes(token.toLowerCase()))

  const initMatch = problemPddl.match(/\(:init([\s\S]*?)\)\s*\(:goal/i)
  const initSection = initMatch ? initMatch[1] : ''

  const onRelations = Array.from(initSection.matchAll(/\(on\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\)/gi)).map(
    (m) => ({ top: m[1], bottom: m[2] })
  )
  const onTable = Array.from(initSection.matchAll(/\(ontable\s+([a-zA-Z0-9_-]+)\)/gi)).map((m) => m[1])

  return {
    blocks,
    onRelations,
    onTable,
  }
}

function rebuildInit(problemPddl: string, state: ParsedState): string {
  const initMatch = problemPddl.match(/\(:init([\s\S]*?)\)\s*\(:goal/i)
  if (!initMatch) return problemPddl

  const oldInitRaw = initMatch[1]
  const preservedLines = oldInitRaw
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line && !/^\(on\s+/i.test(line) && !/^\(ontable\s+/i.test(line))

  const newFacts = [
    ...state.onTable.map((b) => `(ontable ${b})`),
    ...state.onRelations.map((r) => `(on ${r.top} ${r.bottom})`),
  ]

  const merged = [...preservedLines, ...newFacts]
  const initBlock = `\n  ${merged.join('\n  ')}\n `
  return problemPddl.replace(oldInitRaw, initBlock)
}

// ─── Read-only stack visualizer ───────────────────────────────────────────────

function StackVisualizer({ parsed }: { parsed: ParsedState }) {
  // Build columns: each column is a tower from bottom to top
  const columns: string[][] = []
  const placed = new Set<string>()

  // Find all blocks on the table
  for (const b of parsed.onTable) {
    const tower: string[] = [b]
    let current = b
    placed.add(b)
    // Build upward
    while (true) {
      const above = parsed.onRelations.find((r) => r.bottom === current)
      if (!above) break
      tower.push(above.top)
      placed.add(above.top)
      current = above.top
    }
    columns.push(tower)
  }

  // Any blocks not yet placed (only on-relations, no ontable)
  for (const b of parsed.blocks) {
    if (!placed.has(b)) {
      columns.push([b])
    }
  }

  if (columns.length === 0) {
    return <p className="text-xs text-lapis-text-secondary italic">No blocks placed on table.</p>
  }

  return (
    <div className="flex items-end gap-3 min-h-[80px] py-2">
      {columns.map((tower, ci) => (
        <div key={ci} className="flex flex-col-reverse items-center gap-1">
          {tower.map((block, bi) => (
            <div
              key={block}
              className="px-3 py-1.5 rounded border border-lapis-accent/60 bg-lapis-accent/10 text-lapis-accent font-mono text-xs font-semibold min-w-[40px] text-center"
              title={`Block ${block} (layer ${bi + 1})`}
            >
              {block}
            </div>
          ))}
          <div className="w-full h-px bg-lapis-border mt-1" />
          <span className="text-[10px] text-lapis-text-secondary">table</span>
        </div>
      ))}
    </div>
  )
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function BlocksworldEditor({ problemPddl, onChange, readOnly = false }: BlocksworldEditorProps) {
  const parsed = useMemo(() => parseBlocksworld(problemPddl), [problemPddl])
  const [top, setTop] = useState('')
  const [bottom, setBottom] = useState('table')
  const [dragging, setDragging] = useState('')

  const applyRelation = () => {
    if (!top) return
    const nextState: ParsedState = {
      ...parsed,
      onRelations: parsed.onRelations.filter((r) => r.top !== top),
      onTable: parsed.onTable.filter((b) => b !== top),
    }

    if (bottom === 'table') {
      nextState.onTable = [...nextState.onTable, top]
    } else if (bottom !== top) {
      nextState.onRelations = [...nextState.onRelations, { top, bottom }]
    }

    const updated = rebuildInit(problemPddl, nextState)
    onChange(updated)
  }

  // Read-only: just show the visual tower layout
  if (readOnly) {
    return (
      <div className="rounded-xl border border-lapis-border bg-lapis-card p-4 space-y-2">
        <p className="text-xs uppercase tracking-wide text-lapis-text-secondary">State</p>
        <StackVisualizer parsed={parsed} />
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-lapis-border bg-lapis-card p-4 space-y-4">
      <div>
        <p className="text-sm font-semibold text-lapis-text">Blocksworld Visual Editor</p>
        <p className="text-xs text-lapis-text-secondary">Edit stack relationships and sync to PDDL init state.</p>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <select
          className="bg-lapis-bg border border-lapis-border rounded px-2 py-2 text-sm text-lapis-text"
          value={top}
          onChange={(e) => setTop(e.target.value)}
        >
          <option value="">Select block</option>
          {parsed.blocks.map((b) => (
            <option key={b} value={b}>{b}</option>
          ))}
        </select>
        <select
          className="bg-lapis-bg border border-lapis-border rounded px-2 py-2 text-sm text-lapis-text"
          value={bottom}
          onChange={(e) => setBottom(e.target.value)}
        >
          <option value="table">table</option>
          {parsed.blocks.map((b) => (
            <option key={b} value={b}>{b}</option>
          ))}
        </select>
      </div>

      <button
        type="button"
        className="w-full px-3 py-2 rounded-lg bg-lapis-accent text-black text-sm font-semibold disabled:opacity-50"
        disabled={!top}
        onClick={applyRelation}
      >
        Apply Relation
      </button>

      <div className="space-y-2">
        <p className="text-xs uppercase tracking-wide text-lapis-text-secondary">Current Scene</p>
        <StackVisualizer parsed={parsed} />
        <div className="grid grid-cols-1 gap-2">
          {parsed.onTable.map((b) => (
            <div
              key={`table-${b}`}
              draggable
              onDragStart={() => setDragging(b)}
              onDragOver={(event) => event.preventDefault()}
              onDrop={() => {
                if (!dragging) return
                setTop(dragging)
                setBottom('table')
              }}
              className="rounded border border-lapis-border bg-lapis-bg px-3 py-2 text-xs text-lapis-text cursor-grab"
            >
              {b} on table
            </div>
          ))}
          {parsed.onRelations.map((r) => (
            <div
              key={`${r.top}-${r.bottom}`}
              draggable
              onDragStart={() => setDragging(r.top)}
              onDragOver={(event) => event.preventDefault()}
              onDrop={() => {
                if (!dragging) return
                setTop(dragging)
                setBottom(r.bottom)
              }}
              className="rounded border border-lapis-border bg-lapis-bg px-3 py-2 text-xs text-lapis-text cursor-grab"
            >
              {r.top} on {r.bottom}
            </div>
          ))}
        </div>
        <p className="text-[11px] text-lapis-text-secondary">
          Tip: drag any block card and drop onto a target card, then click Apply Relation.
        </p>
      </div>
    </div>
  )
}
