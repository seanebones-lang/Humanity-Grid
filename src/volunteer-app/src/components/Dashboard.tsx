import { TrendingUp, Award, Clock, Target, BarChart3, FlaskConical, Thermometer, Battery } from 'lucide-react'
import { SystemInfo, ThermalInfo, PowerInfo, BoincStatus, ContributionStats } from '@/types'
import { cn } from '@/lib/utils'

interface DashboardProps {
  systemInfo: SystemInfo | null
  thermalInfo: ThermalInfo | null
  powerInfo: PowerInfo | null
  boincStatus: BoincStatus | null
  contributions: ContributionStats | null
}

const statCards = [
  { label: 'Total Hours', value: '0.0', icon: Clock, color: 'text-primary' },
  { label: 'Validated Work Units', value: '0', icon: Target, color: 'text-success' },
  { label: 'Projects Contributed', value: '0', icon: FlaskConical, color: 'text-warning' },
  { label: 'Papers Published', value: '0', icon: Award, color: 'text-primary-light' },
]

export default function Dashboard({ systemInfo, thermalInfo, powerInfo, boincStatus, contributions }: DashboardProps) {
  const maxTemp = thermalInfo?.temperatures.reduce((max, t) => Math.max(max, t.temperature), 0) ?? 0
  const isThermalThrottling = maxTemp > 70

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary/20 via-surface to-background p-6 lg:p-8 border border-primary/20">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,var(--color-primary)/10,transparent_70%)]" />
        <div className="relative z-10">
          <h1 className="text-3xl lg:text-4xl font-bold mb-2 gradient-text">Welcome back</h1>
          <p className="text-text-muted mb-6 max-w-xl">
            Tonight your computer screened <span className="font-bold text-primary">18,421</span> candidate molecules
            for a pediatric cancer study.
          </p>
          <div className="flex flex-wrap gap-3">
            <button className="px-4 py-2 rounded-lg bg-primary text-white font-medium hover:bg-primary-dark transition-colors">
              View Details →
            </button>
            <button className="px-4 py-2 rounded-lg bg-surface-elevated text-text font-medium hover:bg-surface transition-colors border border-border">
              Pause Computing
            </button>
          </div>
        </div>
        <div className="absolute bottom-4 right-4 opacity-10">
          <FlaskConical className="w-32 h-32" />
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, i) => (
          <div key={i} className="glass rounded-xl p-5 border border-border/50">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-text-muted">{stat.label}</p>
                <p className="font-mono text-2xl font-bold mt-1">
                {contributions ? (
                  i === 0 ? contributions.total_hours :
                  i === 1 ? contributions.validated_work_units :
                  i === 2 ? contributions.projects_contributed :
                  contributions.papers_published
                ) : stat.value}
              </p>
              </div>
              <div className={cn('p-2 rounded-lg', stat.color.replace('text-', 'bg-') + '/10')}>
                <stat.icon className={cn('w-5 h-5', stat.color)} />
              </div>
            </div>
            <div className="mt-4 h-1.5 bg-surface rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full" style={{ width: '0%' }} />
            </div>
          </div>
        ))}
      </div>

      {/* Current Activity & System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* BOINC Activity */}
        <div className="glass rounded-xl p-6 border border-border/50">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Current Activity</h2>
            <div className={cn('flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium', boincStatus?.running ? 'bg-success/20 text-success' : 'bg-surface-elevated text-text-muted')}>
              <span className={cn('h-2 w-2 rounded-full', boincStatus?.running ? 'bg-success' : 'bg-text-subtle')} />
              {boincStatus?.running ? 'Computing' : 'Idle'}
            </div>
          </div>

          {boincStatus?.running && boincStatus.active_tasks > 0 ? (
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-3 rounded-lg bg-surface/50">
                  <p className="font-mono text-2xl font-bold">{boincStatus.active_tasks}</p>
                  <p className="text-xs text-text-muted">Active Tasks</p>
                </div>
                <div className="p-3 rounded-lg bg-surface/50">
                  <p className="font-mono text-2xl font-bold">{boincStatus.gpu_tasks}</p>
                  <p className="text-xs text-text-muted">GPU Tasks</p>
                </div>
                <div className="p-3 rounded-lg bg-surface/50">
                  <p className="font-mono text-2xl font-bold">{boincStatus.cpu_tasks}</p>
                  <p className="text-xs text-text-muted">CPU Tasks</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-center">
                <div className="p-3 rounded-lg bg-surface/50">
                  <p className="font-mono text-lg">{boincStatus.download_speed.toFixed(1)} MB/s</p>
                  <p className="text-xs text-text-muted">Download</p>
                </div>
                <div className="p-3 rounded-lg bg-surface/50">
                  <p className="font-mono text-lg">{boincStatus.upload_speed.toFixed(1)} MB/s</p>
                  <p className="text-xs text-text-muted">Upload</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-text-muted">
              <FlaskConical className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No active work units</p>
              <p className="text-sm mt-1">BOINC will fetch work when available</p>
            </div>
          )}
        </div>

        {/* System Health */}
        <div className="glass rounded-xl p-6 border border-border/50">
          <h2 className="font-semibold mb-4">System Health</h2>
          <div className="space-y-4">
            {systemInfo && (
              <>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-primary/10"><TrendingUp className="w-5 h-5 text-primary" /></div>
                    <div>
                      <p className="font-medium">CPU Usage</p>
                      <p className="text-sm text-text-muted">{systemInfo.cpus.length} cores</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-mono text-xl font-bold">{systemInfo.cpu_usage.toFixed(1)}%</p>
                    <p className="text-xs text-text-muted">{(systemInfo.used_memory / systemInfo.total_memory * 100).toFixed(1)}% RAM</p>
                  </div>
                </div>
                <div className="h-2 bg-surface rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-500"
                    style={{ width: `${systemInfo.cpu_usage}%` }}
                  />
                </div>
              </>
            )}

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={cn('p-2 rounded-lg', isThermalThrottling ? 'bg-warning/10' : 'bg-success/10')}>
                  <Thermometer className={cn('w-5 h-5', isThermalThrottling ? 'text-warning' : 'text-success')} />
                </div>
                <div>
                  <p className="font-medium">Temperature</p>
                  <p className="text-sm text-text-muted">Thermal throttling: {isThermalThrottling ? 'Active' : 'Inactive'}</p>
                </div>
              </div>
              <div className="text-right">
                <p className={cn('font-mono text-xl font-bold', isThermalThrottling ? 'text-warning' : 'text-success')}>{maxTemp.toFixed(1)}°C</p>
                <p className="text-xs text-text-muted">Max observed</p>
              </div>
            </div>
            <div className="h-2 bg-surface rounded-full overflow-hidden">
              <div
                className={cn('h-full rounded-full transition-all duration-500', isThermalThrottling ? 'bg-warning' : 'bg-success')}
                style={{ width: `${Math.min(maxTemp / 95 * 100, 100)}%` }}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10"><Battery className="w-5 h-5 text-primary" /></div>
                <div>
                  <p className="font-medium">Power</p>
                  <p className="text-sm text-text-muted">{powerInfo?.on_battery ? 'Battery' : 'AC Power'}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-mono text-xl font-bold">{powerInfo?.battery_percentage ?? 100}%</p>
                <p className="text-xs text-text-muted">{powerInfo?.is_charging ? 'Charging' : 'Discharging'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="glass rounded-xl p-6 border border-border/50">
        <h2 className="font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="p-4 rounded-xl bg-surface/50 border border-border hover:border-primary/50 hover:bg-primary/5 transition-all text-left">
            <div className="p-2 rounded-lg bg-primary/10 mb-3"><BarChart3 className="w-5 h-5 text-primary" /></div>
            <p className="font-medium">View Contributions</p>
            <p className="text-sm text-text-muted mt-1">See your impact</p>
          </button>
          <button className="p-4 rounded-xl bg-surface/50 border border-border hover:border-primary/50 hover:bg-primary/5 transition-all text-left">
            <div className="p-2 rounded-lg bg-success/10 mb-3"><Award className="w-5 h-5 text-success" /></div>
            <p className="font-medium">Project Stories</p>
            <p className="text-sm text-text-muted mt-1">What you've helped</p>
          </button>
          <button className="p-4 rounded-xl bg-surface/50 border border-border hover:border-primary/50 hover:bg-primary/5 transition-all text-left">
            <div className="p-2 rounded-lg bg-warning/10 mb-3"><Target className="w-5 h-5 text-warning" /></div>
            <p className="font-medium">Adjust Resources</p>
            <p className="text-sm text-text-muted mt-1">CPU, GPU, thermal limits</p>
          </button>
          <button className="p-4 rounded-xl bg-surface/50 border border-border hover:border-primary/50 hover:bg-primary/5 transition-all text-left">
            <div className="p-2 rounded-lg bg-primary-light/10 mb-3"><FlaskConical className="w-5 h-5 text-primary-light" /></div>
            <p className="font-medium">Choose Causes</p>
            <p className="text-sm text-text-muted mt-1">Cancer, Alzheimer's, more</p>
          </button>
        </div>
      </div>
    </div>
  )
}

