import { useState } from 'react'
import { Settings, X, Trophy, FlaskConical, Brain, Zap, Dna } from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

import CauseSelector from './components/CauseSelector'
import ResourceControls from './components/ResourceControls'
import Dashboard from './components/Dashboard'
import ProjectStories from './components/ProjectStories'
import TeamLeaderboard from './components/TeamLeaderboard'
import SettingsPanel from './components/SettingsPanel'

// Types
interface SystemInfo {
  cpu_usage: number
  total_memory: number
  used_memory: number
  available_memory: number
  cpus: CpuInfo[]
  gpus: GpuInfo[]
  os: string
  arch: string
}

interface CpuInfo {
  name: string
  usage: number
  frequency: number
}

interface GpuInfo {
  name: string
  vendor: string
  memory_total: number
  memory_used: number
  utilization: number
  temperature: number | null
}

interface ThermalInfo {
  temperatures: TemperatureReading[]
}

interface TemperatureReading {
  label: string
  temperature: number
  max: number | null
  critical: number | null
}

interface PowerInfo {
  on_battery: boolean
  battery_percentage: number
  time_remaining: number | null
  is_charging: boolean
}

interface BoincStatus {
  running: boolean
  connected: boolean
  active_tasks: number
  gpu_tasks: number
  cpu_tasks: number
  download_speed: number
  upload_speed: number
}

interface UserSettings {
  causes: CauseAllocation[]
  cpu_limit_percent: number
  gpu_limit_percent: number
  memory_limit_gb: number
  thermal_limit_celsius: number
  thermal_resume_celsius: number
  run_on_battery: boolean
  schedule: ScheduleConfig
  network_wifi_only: boolean
  network_metered_allowed: boolean
}

interface CauseAllocation {
  id: string
  name: string
  icon: string
  percentage: number
  enabled: boolean
}

interface ScheduleConfig {
  weekday_start: string
  weekday_end: string
  weekend_all_day: boolean
  custom_hours: ScheduleEntry[]
}

interface ScheduleEntry {
  day: string
  start: string
  end: string
}

interface ContributionStats {
  total_hours: number
  validated_work_units: number
  projects_contributed: number
  papers_published: number
  current_streak: number
  total_credits: number
}

interface ProjectStory {
  project_id: string
  title: string
  description: string
  your_contribution: string
  molecules_screened: number
  hours_donated: number
  status: string
}

function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs))
}

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'causes' | 'resources' | 'stories' | 'teams' | 'settings'>('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  // Preview deliberately has no native bridge, telemetry, or volunteer connection.
  const systemInfo: SystemInfo | null = null
  const thermalInfo: ThermalInfo | null = null
  const powerInfo: PowerInfo | null = null
  const boincStatus: BoincStatus | null = null
  const contributions: ContributionStats | null = null
  const projectStories: ProjectStory[] = []
  const [settings, setSettings] = useState<UserSettings>({
    causes: [], cpu_limit_percent: 30, gpu_limit_percent: 0, memory_limit_gb: 4,
    thermal_limit_celsius: 75, thermal_resume_celsius: 65, run_on_battery: false,
    schedule: { weekday_start: '22:00', weekday_end: '06:00', weekend_all_day: false, custom_hours: [] },
    network_wifi_only: true, network_metered_allowed: false,
  })

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: <FlaskConical className="w-5 h-5" /> },
    { id: 'causes', label: 'Causes', icon: <Dna className="w-5 h-5" /> },
    { id: 'resources', label: 'Resources', icon: <Zap className="w-5 h-5" /> },
    { id: 'stories', label: 'Impact', icon: <Trophy className="w-5 h-5" /> },
    { id: 'teams', label: 'Teams', icon: <Brain className="w-5 h-5" /> },
    { id: 'settings', label: 'Settings', icon: <Settings className="w-5 h-5" /> },
  ]

  return (
    <div className="flex h-full w-full bg-background">
      {/* Sidebar */}
      <aside className={cn(
        'fixed inset-y-0 left-0 z-50 w-64 bg-surface border-r border-border transform transition-transform duration-300 ease-in-out',
        sidebarOpen ? 'translate-x-0' : 'invisible -translate-x-full lg:visible lg:translate-x-0'
      )}>
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex h-16 items-center justify-between px-4 border-b border-border">
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                <FlaskConical className="w-5 h-5 text-white" />
              </div>
              <span className="font-semibold text-lg">Humanity Grid</span>
            </div>
            <button
              className="lg:hidden p-2 rounded-md hover:bg-surface-elevated"
              aria-label="Close navigation"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id as typeof activeTab)
                  setSidebarOpen(false)
                }}
                className={cn(
                  'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                  activeTab === tab.id
                    ? 'bg-primary/20 text-primary border border-primary/30'
                    : 'text-text-muted hover:bg-surface-elevated hover:text-text'
                )}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}

            {/* BOINC Status Indicator */}
            <div className="mt-4 rounded-lg border border-border bg-surface-elevated p-3">
              <div className="flex items-center justify-between text-xs text-text-muted mb-2">
                <span>BOINC Status</span>
                <span className={cn(
                  'flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium',
                  false ? 'bg-success/20 text-success' : 'bg-error/20 text-error'
                )}>
                  <span className={cn('h-1.5 w-1.5 rounded-full', false ? 'bg-success' : 'bg-error')} />
                  Not connected
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-center">
                <div>
                  <div className="text-lg font-bold">{0}</div>
                  <div className="text-[11px] text-text-subtle">Active</div>
                </div>
                <div>
                  <div className="text-lg font-bold">{0}</div>
                  <div className="text-[11px] text-text-subtle">GPU</div>
                </div>
              </div>
            </div>
          </nav>

          {/* Footer */}
          <div className="border-t border-border p-4">
            <div className="flex items-center gap-3 text-sm text-text-muted">
              <span className="text-xs">v0.1.0</span>
              <span className="flex-1" />
              <a href="https://github.com/seanebones-lang/Humanity-Grid" target="_blank" rel="noopener noreferrer" className="hover:text-primary">
                GitHub
              </a>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <main className="flex-1 lg:ml-64 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="flex h-14 items-center justify-between px-4 border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-10">
          <button
            className="lg:hidden p-2 rounded-md hover:bg-surface-elevated"
            aria-label="Open navigation"
            onClick={() => setSidebarOpen(true)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div className="flex-1 lg:flex-none" />

          <div className="flex items-center gap-3">
            <button className="p-2 rounded-lg hover:bg-surface-elevated" aria-label="Open settings" onClick={() => setActiveTab('settings')}><Settings className="w-5 h-5" /></button>
          </div>
        </header>

        <div role="status" className="p-4 bg-warning/10 border-b border-warning/30 text-sm">Design preview — no compute jobs, hardware monitoring, account, or BOINC connection. Changes last for this page session and do not affect your computer.</div>
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 lg:p-6">
          {activeTab === 'dashboard' && (
            <Dashboard
              systemInfo={systemInfo}
              thermalInfo={thermalInfo}
              powerInfo={powerInfo}
              boincStatus={boincStatus}
              contributions={contributions}
              onNavigate={setActiveTab}
            />
          )}

          {activeTab === 'causes' && (
            <CauseSelector
              settings={settings}
              onUpdate={setSettings}
            />
          )}

          {activeTab === 'resources' && (
            <ResourceControls
              systemInfo={systemInfo}
              thermalInfo={thermalInfo}
              powerInfo={powerInfo}
              settings={settings}
              onUpdate={setSettings}
            />
          )}

          {activeTab === 'stories' && (
            <ProjectStories
              stories={projectStories}
              contributions={contributions}
            />
          )}

          {activeTab === 'teams' && (
            <TeamLeaderboard />
          )}

          {activeTab === 'settings' && (
            <SettingsPanel
              settings={settings}
              onUpdate={setSettings}
            />
          )}
        </div>
      </main>
    </div>
  )
}

export default App