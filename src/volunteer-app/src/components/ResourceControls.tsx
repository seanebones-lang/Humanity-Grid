import { useState, useEffect } from 'react'
import { Slider } from '@/components/ui'
import { invoke } from '@tauri-apps/api/core'
import { Cpu, MemoryStick, Thermometer, Battery, Wifi, Network, Zap } from 'lucide-react'
import { UserSettings, SystemInfo, ThermalInfo, PowerInfo } from '@/types'

interface ResourceControlsProps {
  systemInfo: SystemInfo | null
  thermalInfo: ThermalInfo | null
  powerInfo: PowerInfo | null
  settings: UserSettings | null
  onUpdate: (settings: UserSettings) => void
}

export default function ResourceControls({ systemInfo, thermalInfo, powerInfo, settings, onUpdate }: ResourceControlsProps) {
  const [localSettings, setLocalSettings] = useState<UserSettings | null>(settings)

  useEffect(() => {
    if (settings) setLocalSettings(settings)
  }, [settings])

  const updateSetting = <K extends keyof UserSettings>(key: K, value: UserSettings[K]) => {
    const newSettings = { ...localSettings, [key]: value } as UserSettings
    setLocalSettings(newSettings)
    onUpdate(newSettings)
  }

  const maxTemp = thermalInfo?.temperatures.reduce((max, t) => Math.max(max, t.temperature), 0) ?? 0
  const avgTemp = thermalInfo?.temperatures.length
    ? thermalInfo.temperatures.reduce((sum, t) => sum + t.temperature, 0) / thermalInfo.temperatures.length
    : 0

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold mb-2">Resource Controls</h1>
        <p className="text-text-muted">Configure how much of your computer's resources Humanity Grid can use.</p>
      </div>

      {/* System Overview */}
      {systemInfo && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10"><Cpu className="w-5 h-5 text-primary" /></div>
              <div>
                <p className="text-sm text-text-muted">CPU Usage</p>
                <p className="font-mono text-xl font-bold">{systemInfo.cpu_usage.toFixed(1)}%</p>
              </div>
            </div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10"><MemoryStick className="w-5 h-5 text-primary" /></div>
              <div>
                <p className="text-sm text-text-muted">Memory Usage</p>
                <p className="font-mono text-xl font-bold">{(systemInfo.used_memory / systemInfo.total_memory * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10"><Thermometer className="w-5 h-5 text-primary" /></div>
              <div>
                <p className="text-sm text-text-muted">Avg Temperature</p>
                <p className="font-mono text-xl font-bold">{avgTemp.toFixed(1)}°C</p>
              </div>
            </div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10"><Battery className="w-5 h-5 text-primary" /></div>
              <div>
                <p className="text-sm text-text-muted">Power</p>
                <p className="font-mono text-xl font-bold">{powerInfo?.on_battery ? 'Battery' : 'AC Power'}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CPU Controls */}
      <div className="glass rounded-xl p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10"><Cpu className="w-5 h-5 text-primary" /></div>
          <h3 className="font-semibold">CPU Limits</h3>
        </div>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Maximum CPU Usage</span>
              <span className="font-mono font-medium">{localSettings?.cpu_limit_percent ?? 30}%</span>
            </div>
            <Slider
              value={[localSettings?.cpu_limit_percent ?? 30]}
              onValueChange={([v]) => updateSetting('cpu_limit_percent', v)}
              max={100}
              step={5}
              className="h-2"
            />
            <p className="text-xs text-text-muted mt-1">Limits BOINC to this percentage of total CPU time. Lower = cooler, quieter.</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-text-muted">CPU Cores Available</label>
              <p className="font-mono text-lg">{systemInfo?.cpus.length ?? 0}</p>
            </div>
            <div>
              <label className="text-sm text-text-muted">Cores at Limit</label>
              <p className="font-mono text-lg">{Math.max(1, Math.round((systemInfo?.cpus.length ?? 1) * ((localSettings?.cpu_limit_percent ?? 30) / 100)))}</p>
            </div>
          </div>
        </div>
      </div>

      {/* GPU Controls */}
      {systemInfo?.gpus.length && systemInfo.gpus.length > 0 && (
        <div className="glass rounded-xl p-6 space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10"><Zap className="w-5 h-5 text-primary" /></div>
            <h3 className="font-semibold">GPU Limits</h3>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Maximum GPU Usage</span>
                <span className="font-mono font-medium">{localSettings?.gpu_limit_percent ?? 40}%</span>
              </div>
              <Slider
                value={[localSettings?.gpu_limit_percent ?? 40]}
                onValueChange={([v]) => updateSetting('gpu_limit_percent', v)}
                max={100}
                step={5}
                className="h-2"
              />
              <p className="text-xs text-text-muted mt-1">Time-slices GPU compute. Requires GPU work units from projects.</p>
            </div>
            <div className="space-y-3">
              {systemInfo.gpus.map((gpu, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-surface/50">
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 rounded bg-primary/10"><Zap className="w-4 h-4 text-primary" /></div>
                    <div>
                      <p className="font-medium">{gpu.name}</p>
                      <p className="text-sm text-text-muted">{gpu.vendor} • {Math.round(gpu.memory_total / 1024 / 1024 / 1024)} GB VRAM</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-mono">{gpu.utilization.toFixed(0)}% used</p>
                    {gpu.temperature && <p className="text-sm text-text-muted">{gpu.temperature.toFixed(1)}°C</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Memory Controls */}
      <div className="glass rounded-xl p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10"><MemoryStick className="w-5 h-5 text-primary" /></div>
          <h3 className="font-semibold">Memory Limits</h3>
        </div>
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span>Maximum RAM Usage</span>
            <span className="font-mono font-medium">{localSettings?.memory_limit_gb ?? 8} GB</span>
          </div>
          <Slider
            value={[localSettings?.memory_limit_gb ?? 8]}
            onValueChange={([v]) => updateSetting('memory_limit_gb', v)}
            max={Math.floor((systemInfo?.total_memory ?? 16 * 1024 * 1024 * 1024) / 1024 / 1024 / 1024)}
            step={1}
            className="h-2"
          />
          <p className="text-xs text-text-muted mt-1">Hard limit on RAM for BOINC tasks. Prevents system slowdown.</p>
        </div>
      </div>

      {/* Thermal Controls */}
      <div className="glass rounded-xl p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10"><Thermometer className="w-5 h-5 text-primary" /></div>
          <h3 className="font-semibold">Thermal Protection</h3>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Pause Above</span>
              <span className="font-mono font-medium">{localSettings?.thermal_limit_celsius ?? 75}°C</span>
            </div>
            <Slider
              value={[localSettings?.thermal_limit_celsius ?? 75]}
              onValueChange={([v]) => updateSetting('thermal_limit_celsius', v)}
              max={95}
              min={50}
              step={1}
              className="h-2"
            />
            <p className="text-xs text-text-muted mt-1">Current max: {maxTemp.toFixed(1)}°C</p>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Resume Below</span>
              <span className="font-mono font-medium">{localSettings?.thermal_resume_celsius ?? 65}°C</span>
            </div>
            <Slider
              value={[localSettings?.thermal_resume_celsius ?? 65]}
              onValueChange={([v]) => updateSetting('thermal_resume_celsius', v)}
              max={90}
              min={40}
              step={1}
              className="h-2"
            />
            <p className="text-xs text-text-muted mt-1">Hysteresis prevents rapid pause/resume cycles</p>
          </div>
        </div>
        <div className="h-3 bg-surface rounded-full overflow-hidden relative">
          <div
            className="absolute top-0 bottom-0 bg-warning/50"
            style={{ left: `${(localSettings?.thermal_resume_celsius ?? 65) / 95 * 100}%`, width: `${((localSettings?.thermal_limit_celsius ?? 75) - (localSettings?.thermal_resume_celsius ?? 65)) / 95 * 100}%` }}
          />
          <div
            className="absolute top-0 bottom-0 bg-error/50"
            style={{ left: `${(localSettings?.thermal_limit_celsius ?? 75) / 95 * 100}%`, right: 0 }}
          />
          <div className="relative h-full flex items-center justify-between px-2 text-xs text-text-subtle">
            <span>40°C</span>
            <span>95°C</span>
          </div>
        </div>
      </div>

      {/* Power Controls */}
      <div className="glass rounded-xl p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10"><Battery className="w-5 h-5 text-primary" /></div>
          <h3 className="font-semibold">Power Management</h3>
        </div>
        <div className="space-y-4">
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <p className="font-medium">Pause on Battery</p>
              <p className="text-sm text-text-muted">Only compute when plugged into AC power</p>
            </div>
            <input
              type="checkbox"
              checked={localSettings?.run_on_battery === false}
              onChange={(e) => updateSetting('run_on_battery', !e.target.checked)}
              className="w-5 h-5 accent-primary rounded border-border bg-surface"
            />
          </label>
          {powerInfo && (
            <div className="grid grid-cols-2 gap-4 p-3 rounded-lg bg-surface/50">
              <div className="text-center">
                <p className="font-mono text-2xl">{powerInfo.battery_percentage}%</p>
                <p className="text-sm text-text-muted">Battery</p>
              </div>
              <div className="text-center">
                <p className="font-mono text-2xl">{powerInfo.is_charging ? 'Charging' : 'Discharging'}</p>
                <p className="text-sm text-text-muted">Status</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Network Controls */}
      <div className="glass rounded-xl p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10"><Wifi className="w-5 h-5 text-primary" /></div>
          <h3 className="font-semibold">Network Preferences</h3>
        </div>
        <div className="space-y-3">
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <p className="font-medium">WiFi Only</p>
              <p className="text-sm text-text-muted">Don't use metered/cellular connections</p>
            </div>
            <input
              type="checkbox"
              checked={localSettings?.network_wifi_only ?? true}
              onChange={(e) => updateSetting('network_wifi_only', e.target.checked)}
              className="w-5 h-5 accent-primary rounded border-border bg-surface"
            />
          </label>
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <p className="font-medium">Allow Metered Networks</p>
              <p className="text-sm text-text-muted">Allow downloads on metered connections (may incur charges)</p>
            </div>
            <input
              type="checkbox"
              checked={localSettings?.network_metered_allowed ?? false}
              onChange={(e) => updateSetting('network_metered_allowed', e.target.checked)}
              className="w-5 h-5 accent-primary rounded border-border bg-surface"
            />
          </label>
        </div>
      </div>

      {/* Schedule Controls */}
      <div className="glass rounded-xl p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10"><Network className="w-5 h-5 text-primary" /></div>
          <h3 className="font-semibold">Compute Schedule</h3>
        </div>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-text-muted">Weekdays Start</label>
              <input
                type="time"
                value={localSettings?.schedule.weekday_start ?? '22:00'}
                onChange={(e) => updateSetting('schedule', { ...localSettings!.schedule, weekday_start: e.target.value })}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-surface border border-border text-text focus:border-primary focus:outline-none"
              />
            </div>
            <div>
              <label className="text-sm text-text-muted">Weekdays End</label>
              <input
                type="time"
                value={localSettings?.schedule.weekday_end ?? '07:00'}
                onChange={(e) => updateSetting('schedule', { ...localSettings!.schedule, weekday_end: e.target.value })}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-surface border border-border text-text focus:border-primary focus:outline-none"
              />
            </div>
          </div>
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <p className="font-medium">Weekends: All Day</p>
              <p className="text-sm text-text-muted">Run compute 24/7 on weekends</p>
            </div>
            <input
              type="checkbox"
              checked={localSettings?.schedule.weekend_all_day ?? true}
              onChange={(e) => updateSetting('schedule', { ...localSettings!.schedule, weekend_all_day: e.target.checked })}
              className="w-5 h-5 accent-primary rounded border-border bg-surface"
            />
          </label>
        </div>
      </div>
    </div>
  )
}