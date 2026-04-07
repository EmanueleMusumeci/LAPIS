import { useMemo, useState } from 'react'

interface GridworldEditorProps {
  problemPddl: string
  onChange: (updatedProblemPddl: string) => void
}

interface ParsedGrid {
  rooms: string[]
  agentRoom: string
  objectsByRoom: Record<string, string[]>
}

function parseGrid(problemPddl: string): ParsedGrid {
  const objectsMatch = problemPddl.match(/\(:objects([\s\S]*?)\)/i)
  const objectSection = objectsMatch ? objectsMatch[1] : ''
  const rooms = Array.from(objectSection.matchAll(/([a-zA-Z0-9_-]+)\s*-\s*room/gi)).map((m) => m[1])

  const agentMatch = problemPddl.match(/\(agentinroom\s+([a-zA-Z0-9_-]+)\)/i)
  const agentRoom = agentMatch ? agentMatch[1] : ''

  const objectsByRoom: Record<string, string[]> = {}
  for (const room of rooms) objectsByRoom[room] = []

  for (const m of Array.from(problemPddl.matchAll(/\(objectinroom\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\)/gi))) {
    const obj = m[1]
    const room = m[2]
    if (!objectsByRoom[room]) objectsByRoom[room] = []
    objectsByRoom[room].push(obj)
  }

  return { rooms, agentRoom, objectsByRoom }
}

function replaceAgentRoom(problemPddl: string, room: string): string {
  return problemPddl.replace(/\(agentinroom\s+[a-zA-Z0-9_-]+\)/i, `(agentinroom ${room})`)
}

export default function GridworldEditor({ problemPddl, onChange }: GridworldEditorProps) {
  const parsed = useMemo(() => parseGrid(problemPddl), [problemPddl])
  const [selectedRoom, setSelectedRoom] = useState(parsed.agentRoom || parsed.rooms[0] || '')

  const moveAgent = () => {
    if (!selectedRoom) return
    onChange(replaceAgentRoom(problemPddl, selectedRoom))
  }

  return (
    <div className="rounded-xl border border-lapis-border bg-lapis-card p-4 space-y-4">
      <div>
        <p className="text-sm font-semibold text-lapis-text">Gridworld Visual Editor</p>
        <p className="text-xs text-lapis-text-secondary">Move the agent between rooms and sync to PDDL.</p>
      </div>

      <div className="flex gap-2">
        <select
          className="flex-1 bg-lapis-bg border border-lapis-border rounded px-2 py-2 text-sm text-lapis-text"
          value={selectedRoom}
          onChange={(e) => setSelectedRoom(e.target.value)}
        >
          {parsed.rooms.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        <button
          type="button"
          className="px-3 py-2 rounded-lg bg-lapis-accent text-black text-sm font-semibold disabled:opacity-50"
          disabled={!selectedRoom}
          onClick={moveAgent}
        >
          Move Agent
        </button>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {parsed.rooms.map((room) => (
          <div key={room} className="rounded-lg border border-lapis-border bg-lapis-bg p-3">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-semibold text-lapis-text">{room}</p>
              {parsed.agentRoom === room && (
                <span className="text-[10px] px-2 py-0.5 rounded bg-lapis-accent/20 text-lapis-accent border border-lapis-accent/30">AGENT</span>
              )}
            </div>
            <div className="space-y-1">
              {(parsed.objectsByRoom[room] || []).map((obj) => (
                <div key={`${room}-${obj}`} className="text-xs text-lapis-text-secondary border border-lapis-border/60 rounded px-2 py-1">
                  {obj}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
