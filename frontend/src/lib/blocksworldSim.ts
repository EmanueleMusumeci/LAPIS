/**
 * blocksworldSim.ts — Pure TypeScript blocksworld state simulator.
 *
 * Parses an initial state from PDDL, applies sequences of PDDL actions,
 * and returns problem PDDL strings for each step (for use with BlocksworldEditor).
 */

export interface BWState {
  onTable: string[]
  onRelations: Array<{ top: string; bottom: string }>
}

/** Normalize a planner action string to PDDL format: (action p1 p2 ...) */
export function normalizeAction(raw: string): string {
  const t = raw.trim()
  // Already PDDL: (action p1 p2)
  if (t.startsWith('(') && t.endsWith(')')) return t
  // unified-planning format: stack(b1, b2) → (stack b1 b2)
  const up = t.match(/^([\w-]+)\(([^)]*)\)\s*$/)
  if (up) {
    const params = up[2].split(',').map((s) => s.trim()).filter(Boolean).join(' ')
    return `(${up[1]}${params ? ' ' + params : ''})`
  }
  // bare: action p1 p2 → (action p1 p2)
  return `(${t})`
}

/** Parse initial blocksworld state from problem PDDL. */
export function parseBWInitState(problemPddl: string): BWState {
  const initMatch = problemPddl.match(/\(:init([\s\S]*?)\)\s*\(:goal/i)
  const init = initMatch ? initMatch[1] : ''

  const onRelations = Array.from(init.matchAll(/\(\s*on\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s*\)/gi)).map(
    (m) => ({ top: m[1].toLowerCase(), bottom: m[2].toLowerCase() })
  )
  const onTable = Array.from(init.matchAll(/\(\s*ontable\s+([a-zA-Z0-9_-]+)\s*\)/gi)).map((m) =>
    m[1].toLowerCase()
  )

  return { onTable, onRelations }
}

/** Apply one PDDL action to a blocksworld state, returning the new state. */
export function applyBWAction(state: BWState, action: string): BWState {
  const normalized = normalizeAction(action)
  const clean = normalized.replace(/^\(|\)$/g, '').trim()
  const parts = clean.split(/\s+/)
  const name = (parts[0] || '').toLowerCase()
  const p = parts.slice(1).map((s) => s.toLowerCase())

  let { onTable, onRelations } = state

  switch (name) {
    case 'pick-up':
    case 'pickup': {
      // Remove b from table
      onTable = onTable.filter((x) => x !== p[0])
      break
    }
    case 'put-down':
    case 'putdown': {
      // Place b on table
      if (!onTable.includes(p[0])) onTable = [...onTable, p[0]]
      break
    }
    case 'stack': {
      // p[0] goes on top of p[1]
      onRelations = onRelations.filter((r) => !(r.top === p[0]))
      onRelations = [...onRelations, { top: p[0], bottom: p[1] }]
      onTable = onTable.filter((x) => x !== p[0])
      break
    }
    case 'unstack': {
      // p[0] is picked up from p[1]
      onRelations = onRelations.filter((r) => !(r.top === p[0] && r.bottom === p[1]))
      break
    }
    default:
      break
  }

  return { onTable, onRelations }
}

/** Compute state sequence: states[i] = state AFTER applying actions[0..i-1]. */
export function computeStateSequence(initState: BWState, actions: string[]): BWState[] {
  const states: BWState[] = [initState]
  for (const action of actions) {
    states.push(applyBWAction(states[states.length - 1], action))
  }
  return states // length = actions.length + 1 (index 0 = before any action)
}

/** Rebuild the (:init ...) section of a problem PDDL with a new blocksworld state. */
export function rebuildBWInit(problemPddl: string, state: BWState): string {
  const initMatch = problemPddl.match(/(\(:init)([\s\S]*?)(\)\s*\(:goal)/i)
  if (!initMatch) return problemPddl

  const oldInit = initMatch[2]
  // Preserve non-on/ontable facts (arm-empty, clear, etc.)
  const preserved = oldInit
    .split('\n')
    .map((l) => l.trim())
    .filter(
      (l) =>
        l &&
        !/^\(\s*on\s+/i.test(l) &&
        !/^\(\s*ontable\s+/i.test(l) &&
        !/^\(\s*clear\s+/i.test(l) &&
        !/^\(\s*arm-empty/i.test(l) &&
        !/^\(\s*holding\s+/i.test(l)
    )

  const newFacts = [
    ...state.onTable.map((b) => `(ontable ${b})`),
    ...state.onRelations.map((r) => `(on ${r.top} ${r.bottom})`),
  ]

  const newInit = `\n  ${[...preserved, ...newFacts].join('\n  ')}\n `
  return problemPddl.replace(initMatch[2], newInit)
}
