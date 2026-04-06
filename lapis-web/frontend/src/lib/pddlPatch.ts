export function upsertInitPredicate(problemPddl: string, predicate: string): string {
  const normalized = predicate.trim().replace(/\s+/g, ' ')
  if (!/^\(.+\)$/.test(normalized)) {
    return problemPddl
  }

  const initMatch = problemPddl.match(/\(:init([\s\S]*?)\)\s*\(:goal/i)
  if (!initMatch) {
    return problemPddl
  }

  const initContent = initMatch[1]
  const factMatch = normalized.match(/^\(([a-zA-Z0-9_-]+)(?:\s+([a-zA-Z0-9_-]+))?/)
  if (!factMatch) {
    return problemPddl
  }

  const predicateName = factMatch[1]
  const entityKey = factMatch[2] || ''

  const keptLines = initContent
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .filter((line) => {
      if (!line.startsWith('(')) return true
      const lineMatch = line.match(/^\(([a-zA-Z0-9_-]+)(?:\s+([a-zA-Z0-9_-]+))?/)
      if (!lineMatch) return true
      if (lineMatch[1] !== predicateName) return true
      if (!entityKey) return false
      return lineMatch[2] !== entityKey
    })

  const nextFacts = [...keptLines, normalized]
  const newInit = `\n  ${nextFacts.join('\n  ')}\n `
  return problemPddl.replace(initContent, newInit)
}

export function extractIssueLine(problemText: string, issue: string): number | null {
  const token = issue.match(/[a-zA-Z0-9_-]+/)?.[0]
  if (!token) return null

  const lines = problemText.split('\n')
  for (let i = 0; i < lines.length; i += 1) {
    if (lines[i].toLowerCase().includes(token.toLowerCase())) {
      return i + 1
    }
  }
  return null
}
