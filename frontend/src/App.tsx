import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { Activity, BarChart3, Bot } from 'lucide-react'
import LiveExecution from './pages/LiveExecution'
import ModelRace from './pages/ModelRace'
import AgenticEditor from './pages/AgenticEditor'
import { ApiKeyProvider } from './contexts/ApiKeyContext'

function Header() {
  return (
    <header className="border-b border-lapis-border bg-lapis-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl font-extrabold tracking-wide text-lapis-accent">
            LAPIS
          </span>
          <span className="text-sm text-lapis-muted italic hidden sm:block">
            Language-to-Action Planning via Iterative Schema injection
          </span>
        </div>

        <nav className="flex items-center gap-1">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-lapis-accent/20 text-lapis-accent'
                  : 'text-lapis-text-secondary hover:bg-lapis-card hover:text-lapis-text'
              }`
            }
          >
            <Activity className="w-4 h-4" />
            <span className="hidden sm:inline">Live Execution</span>
          </NavLink>

          <NavLink
            to="/race"
            className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-lapis-accent/20 text-lapis-accent'
                  : 'text-lapis-text-secondary hover:bg-lapis-card hover:text-lapis-text'
              }`
            }
          >
            <BarChart3 className="w-4 h-4" />
            <span className="hidden sm:inline">Model Race</span>
          </NavLink>

          <NavLink
            to="/editor"
            className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-lapis-accent/20 text-lapis-accent'
                  : 'text-lapis-text-secondary hover:bg-lapis-card hover:text-lapis-text'
              }`
            }
          >
            <Bot className="w-4 h-4" />
            <span className="hidden sm:inline">Agentic Editor</span>
          </NavLink>
        </nav>
      </div>
    </header>
  )
}

function App() {
  return (
    <ApiKeyProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col">
          <Header />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<LiveExecution />} />
              <Route path="/race" element={<ModelRace />} />
              <Route path="/editor" element={<AgenticEditor />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ApiKeyProvider>
  )
}

export default App
