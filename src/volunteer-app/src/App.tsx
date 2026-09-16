import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Settings, User, X, ChevronDown, ChevronUp, Pause, Play, Info, Trophy, FlaskConical, Brain, Bug, Globe, Zap, Dna } from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

import CauseSelector from './components/CauseSelector'
import ResourceControls from './components/ResourceControls'
import ThermalMonitor from './components/ThermalMonitor'
import PowerSchedule from './components/PowerSchedule'
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

const CAUSE_ICONS: Record<string, React.ReactNode> = {
  cancer: <Dna className="w-5 h-5" />,
  alzheimer: <Brain className="w-5 h-5" />,
  antibiotics: <Bug className="w-5 h-5" />,
  climate: <Globe className="w-5 h-5" />,
  energy: <Zap className="w-5 h-5" />,
  rare: <FlaskConical className="w-5 h-5" />,
}

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'causes' | 'resources' | 'stories' | 'teams' | 'settings'>('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null)
  const [thermalInfo, setThermalInfo] = useState<ThermalInfo | null>(null)
  const [powerInfo, setPowerInfo] = useState<PowerInfo | null>(null)
  const [boincStatus, setBoincStatus] = useState<BoincStatus | null>(null)
  const [settings, setSettings] = useState<UserSettings | null>(null)
  const [contributions, setContributions] = useState<ContributionStats | null>(null)
  const [projectStories, setProjectStories] = useState<ProjectStory[]>([])
  const [loading, setLoading] = useState(true)

  // Load initial data
  useEffect(() => {
    async function loadData() {
      try {
        const [sys, therm, power, boinc, sett, contrib, stories] = await Promise.all([
          invoke<SystemInfo>('get_system_info'),
          invoke<ThermalInfo>('get_thermal_info'),
          invoke<PowerInfo>('get_power_info'),
          invoke<BoincStatus>('boinc_get_status'),
          invoke<UserSettings>('get_settings'),
          invoke<ContributionStats>('get_contributions'),
          invoke<ProjectStory[]>('get_project_stories'),
        ])
        setSystemInfo(sys)
        setThermalInfo(therm)
        setPowerInfo(power)
        setBoincStatus(boinc)
        setSettings(sett)
        setContributions(contrib)
        setProjectStories(stories)
      } catch (e) {
        console.error('Failed to load data:', e)
      } finally {
        setLoading(false)
      }
    }
    loadData()

    // Refresh system info every 5 seconds
    const interval = setInterval(() => {
      invoke<SystemInfo>('get_system_info').then(setSystemInfo).catch(console.error)
      invoke<ThermalInfo>('get_thermal_info').then(setThermalInfo).catch(console.error)
      invoke<PowerInfo>('get_power_info').then(setPowerInfo).catch(console.error)
      invoke<BoincStatus>('boinc_get_status').then(setBoincStatus).catch(console.error)
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-pulse-soft text-primary text-xl">Humanity Grid</div>
      </div>
    )
  }

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
        sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
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
                  boincStatus?.running ? 'bg-success/20 text-success' : 'bg-error/20 text-error'
                )}>
                  <span className={cn('h-1.5 w-1.5 rounded-full', boincStatus?.running ? 'bg-success' : 'bg-error')} />
                  {boincStatus?.running ? 'Running' : 'Stopped'}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-center">
                <div>
                  <div className="text-lg font-bold">{boincStatus?.active_tasks ?? 0}</div>
                  <div className="text-[11px] text-text-subtle">Active</div>
                </div>
                <div>
                  <div className="text-lg font-bold">{boincStatus?.gpu_tasks ?? 0}</div>
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
            onClick={() => setSidebarOpen(true)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div className="flex-1 lg:flex-none" />

          <div className="flex items-center gap-3">
            {/* System quick stats */}
            {systemInfo && (
              <div className="hidden sm:flex items-center gap-4 text-xs text-text-muted">
                <div className="flex items-center gap-1">
                  <span className={cn('h-2 w-2 rounded-full', systemInfo.cpu_usage > 80 ? 'bg-error' : systemInfo.cpu_usage > 50 ? 'bg-warning' : 'bg-success')} />
                  <span>{systemInfo.cpu_usage.toFixed(0)}% CPU</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className={cn('h-2 w-2 rounded-full', 
                    (systemInfo.used_memory / systemInfo.total_memory) > 0.8 ? 'bg-error' : 
                    (systemInfo.used_memory / systemInfo.total_memory) > 0.5 ? 'bg-warning' : 'bg-success')} />
                  <span>{(systemInfo.used_memory / systemInfo.total_memory * 100).toFixed(0)}% RAM</span>
                </div>
              </div>
            )}

            <div className="flex items-center gap-2">
              <button className="p-2 rounded-lg hover:bg-surface-elevated" title="Settings">
                <Settings className="w-5 h-5" />
              </button>
              <button className="p-2 rounded-lg hover:bg-surface-elevated" title="Profile">
                <User className="w-5 h-5" />
              </button>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 lg:p-6">
          {activeTab === 'dashboard' && (
            <Dashboard
              systemInfo={systemInfo}
              thermalInfo={thermalInfo}
              powerInfo={powerInfo}
              boincStatus={boincStatus}
              contributions={contributions}
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