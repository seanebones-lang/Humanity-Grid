import { UserSettings } from '@/types'
import { invoke } from '@tauri-apps/api/core'
import { Save, Loader2, Shield, Globe, Bell, Palette, Key, Database, Trash2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState } from 'react'

interface SettingsPanelProps {
  settings: UserSettings | null
  onUpdate: (settings: UserSettings) => void
}

export default function SettingsPanel({ settings, onUpdate }: SettingsPanelProps) {
  const [localSettings, setLocalSettings] = useState<UserSettings | null>(settings)
  const [saving, setSaving] = useState(false)
  const [activeSection, setActiveSection] = useState<'general' | 'compute' | 'network' | 'notifications' | 'appearance' | 'advanced'>('general')

  const updateSetting = <K extends keyof UserSettings>(key: K, value: UserSettings[K]) => {
    const newSettings = { ...localSettings, [key]: value } as UserSettings
    setLocalSettings(newSettings)
    onUpdate(newSettings)
  }

  const handleSave = async () => {
    if (!localSettings) return
    setSaving(true)
    try {
      // TODO: Save to Tauri backend
      await invoke('update_settings', { settings: localSettings })
    } catch (e) {
      console.error('Failed to save settings:', e)
    } finally {
      setSaving(false)
    }
  }

  const sections = [
    { id: 'general', label: 'General', icon: Shield },
    { id: 'compute', label: 'Compute', icon: Database },
    { id: 'network', label: 'Network', icon: Globe },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'advanced', label: 'Advanced', icon: Key },
  ]

  if (!localSettings) return null

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-2">Settings</h1>
          <p className="text-text-muted">Configure your Humanity Grid experience.</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-4 py-2 rounded-lg bg-primary text-white font-medium hover:bg-primary-dark transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      <div className="glass rounded-xl border border-border/50 overflow-hidden">
        {/* Sidebar Navigation */}
        <div className="flex">
          <nav className="w-48 border-r border-border/50 bg-surface/30 p-4">
            <ul className="space-y-1">
              {sections.map((section) => (
                <li key={section.id}>
                  <button
                    onClick={() => setActiveSection(section.id as typeof activeSection)}
                    className={cn(
                      'flex w-full items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                      activeSection === section.id
                        ? 'bg-primary/20 text-primary border border-primary/30'
                        : 'text-text-muted hover:bg-surface-elevated hover:text-text'
                    )}
                  >
                    <section.icon className="w-5 h-5 flex-shrink-0" />
                    {section.label}
                  </button>
                </li>
              ))}
            </ul>
          </nav>

          {/* Content */}
          <div className="flex-1 p-6 lg:p-8 overflow-y-auto">
            {activeSection === 'general' && (
              <div className="space-y-6 max-w-2xl">
                <h2 className="text-lg font-semibold">General Settings</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Your Name</label>
                    <input
                      type="text"
                      placeholder="Anonymous Volunteer"
                      className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-text focus:border-primary focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Email (optional)</label>
                    <p className="text-sm text-text-muted">For project updates and milestone notifications</p>
                    <input
                      type="email"
                      placeholder="you@example.com"
                      className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-text focus:border-primary focus:outline-none mt-1"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Anonymous Mode</p>
                      <p className="text-sm text-text-muted">Hide your name from leaderboards</p>
                    </div>
                    <input type="checkbox" defaultChecked className="w-5 h-5 accent-primary rounded border-border bg-surface" />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Auto-start on Login</p>
                      <p className="text-sm text-text-muted">Start Humanity Grid when you sign in</p>
                    </div>
                    <input type="checkbox" defaultChecked className="w-5 h-5 accent-primary rounded border-border bg-surface" />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Minimize to Tray</p>
                      <p className="text-sm text-text-muted">Keep running in background when closed</p>
                    </div>
                    <input type="checkbox" checked className="w-5 h-5 accent-primary rounded border-border bg-surface" />
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'compute' && (
              <div className="space-y-6 max-w-2xl">
                <h2 className="text-lg font-semibold">Compute Resources</h2>
                <p className="text-text-muted">These settings control how much of your hardware Humanity Grid can use.</p>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>CPU Limit</span>
                      <span className="font-mono">{localSettings.cpu_limit_percent}%</span>
                    </div>
                    <input
                      type="range"
                      min="5"
                      max="100"
                      step="5"
                      value={localSettings.cpu_limit_percent}
                      onChange={(e) => updateSetting('cpu_limit_percent', Number(e.target.value))}
                      className="w-full h-2 bg-surface rounded-full appearance-none accent-primary"
                    />
                    <p className="text-xs text-text-muted mt-1">Percentage of total CPU time available to BOINC</p>
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>GPU Limit</span>
                      <span className="font-mono">{localSettings.gpu_limit_percent}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      step="5"
                      value={localSettings.gpu_limit_percent}
                      onChange={(e) => updateSetting('gpu_limit_percent', Number(e.target.value))}
                      className="w-full h-2 bg-surface rounded-full appearance-none accent-primary"
                    />
                    <p className="text-xs text-text-muted mt-1">Time-slice GPU compute (requires GPU work units)</p>
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Memory Limit</span>
                      <span className="font-mono">{localSettings.memory_limit_gb} GB</span>
                    </div>
                    <input
                      type="range"
                      min="1"
                      max="64"
                      step="1"
                      value={localSettings.memory_limit_gb}
                      onChange={(e) => updateSetting('memory_limit_gb', Number(e.target.value))}
                      className="w-full h-2 bg-surface rounded-full appearance-none accent-primary"
                    />
                    <p className="text-xs text-text-muted mt-1">Hard RAM limit for BOINC tasks</p>
                  </div>
                </div>

                <div className="pt-4 border-t border-border/50">
                  <h3 className="font-medium mb-4">Thermal Protection</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Pause Above</span>
                        <span className="font-mono">{localSettings.thermal_limit_celsius}°C</span>
                      </div>
                      <input
                        type="range"
                        min="50"
                        max="95"
                        step="1"
                        value={localSettings.thermal_limit_celsius}
                        onChange={(e) => updateSetting('thermal_limit_celsius', Number(e.target.value))}
                        className="w-full h-2 bg-surface rounded-full appearance-none accent-warning"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Resume Below</span>
                        <span className="font-mono">{localSettings.thermal_resume_celsius}°C</span>
                      </div>
                      <input
                        type="range"
                        min="40"
                        max="90"
                        step="1"
                        value={localSettings.thermal_resume_celsius}
                        onChange={(e) => updateSetting('thermal_resume_celsius', Number(e.target.value))}
                        className="w-full h-2 bg-surface rounded-full appearance-none accent-success"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'network' && (
              <div className="space-y-6 max-w-2xl">
                <h2 className="text-lg font-semibold">Network Preferences</h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">WiFi Only</p>
                      <p className="text-sm text-text-muted">Don't use metered/cellular connections</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={localSettings.network_wifi_only}
                      onChange={(e) => updateSetting('network_wifi_only', e.target.checked)}
                      className="w-5 h-5 accent-primary rounded border-border bg-surface"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Allow Metered Networks</p>
                      <p className="text-sm text-text-muted">Allow downloads on metered connections (may incur charges)</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={localSettings.network_metered_allowed}
                      onChange={(e) => updateSetting('network_metered_allowed', e.target.checked)}
                      className="w-5 h-5 accent-primary rounded border-border bg-surface"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Pause on Battery</p>
                      <p className="text-sm text-text-muted">Only compute when plugged into AC power</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={!localSettings.run_on_battery}
                      onChange={(e) => updateSetting('run_on_battery', !e.target.checked)}
                      className="w-5 h-5 accent-primary rounded border-border bg-surface"
                    />
                  </div>
                </div>

                <div className="pt-4 border-t border-border/50">
                  <h3 className="font-medium mb-4">Compute Schedule</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-text-muted mb-1">Weekdays Start</label>
                      <input
                        type="time"
                        value={localSettings.schedule.weekday_start}
                        onChange={(e) => updateSetting('schedule', { ...localSettings.schedule, weekday_start: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-text focus:border-primary focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-text-muted mb-1">Weekdays End</label>
                      <input
                        type="time"
                        value={localSettings.schedule.weekday_end}
                        onChange={(e) => updateSetting('schedule', { ...localSettings.schedule, weekday_end: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-text focus:border-primary focus:outline-none"
                      />
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-4">
                    <div>
                      <p className="font-medium">Weekends: All Day</p>
                      <p className="text-sm text-text-muted">Run compute 24/7 on weekends</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={localSettings.schedule.weekend_all_day}
                      onChange={(e) => updateSetting('schedule', { ...localSettings.schedule, weekend_all_day: e.target.checked })}
                      className="w-5 h-5 accent-primary rounded border-border bg-surface"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'notifications' && (
              <div className="space-y-6 max-w-2xl">
                <h2 className="text-lg font-semibold">Notifications</h2>
                
                <div className="space-y-4">
                  {[
                    { id: 'work_complete', label: 'Work Unit Completed', desc: 'Notify when a work unit finishes' },
                    { id: 'milestone', label: 'Project Milestones', desc: 'Major project updates and publications' },
                    { id: 'thermal', label: 'Thermal Throttling', desc: 'Alert when compute pauses due to temperature' },
                    { id: 'new_project', label: 'New Projects', desc: 'Announcements of new research projects' },
                    { id: 'team_invite', label: 'Team Invitations', desc: 'When someone invites you to a team' },
                    { id: 'weekly_summary', label: 'Weekly Summary', desc: 'Your weekly contribution report' },
                  ].map((notif) => (
                    <div key={notif.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{notif.label}</p>
                        <p className="text-sm text-text-muted">{notif.desc}</p>
                      </div>
                      <input type="checkbox" defaultChecked className="w-5 h-5 accent-primary rounded border-border bg-surface" />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeSection === 'appearance' && (
              <div className="space-y-6 max-w-2xl">
                <h2 className="text-lg font-semibold">Appearance</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Theme</label>
                    <div className="flex gap-3">
                      <button className="flex-1 px-4 py-2 rounded-lg bg-primary text-white font-medium border-2 border-primary">
                        Dark
                      </button>
                      <button className="flex-1 px-4 py-2 rounded-lg bg-surface border border-border text-text font-medium hover:border-primary/50">
                        Light
                      </button>
                      <button className="flex-1 px-4 py-2 rounded-lg bg-surface border border-border text-text font-medium hover:border-primary/50">
                        System
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Accent Color</label>
                    <div className="flex gap-2 flex-wrap">
                      {['#0ea5e9', '#22c55e', '#f59e0b', '#ef4444', '#a855f7', '#ec4899', '#14b8a6'].map((color) => (
                        <button
                          key={color}
                          className="w-10 h-10 rounded-full border-2 transition-all"
                          style={{ backgroundColor: color, borderColor: color }}
                        />
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Animations</p>
                      <p className="text-sm text-text-muted">Enable UI transitions and micro-animations</p>
                    </div>
                    <input type="checkbox" defaultChecked className="w-5 h-5 accent-primary rounded border-border bg-surface" />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Compact Mode</p>
                      <p className="text-sm text-text-muted">Reduce padding and spacing</p>
                    </div>
                    <input type="checkbox" className="w-5 h-5 accent-primary rounded border-border bg-surface" />
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'advanced' && (
              <div className="space-y-6 max-w-2xl">
                <h2 className="text-lg font-semibold">Advanced</h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Developer Mode</p>
                      <p className="text-sm text-text-muted">Show debug info and enable dev tools</p>
                    </div>
                    <input type="checkbox" className="w-5 h-5 accent-primary rounded border-border bg-surface" />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Verbose Logging</p>
                      <p className="text-sm text-text-muted">Detailed logs for troubleshooting</p>
                    </div>
                    <input type="checkbox" className="w-5 h-5 accent-primary rounded border-border bg-surface" />
                  </div>

                  <div className="pt-4 border-t border-border/50">
                    <h3 className="font-medium mb-3">Data Management</h3>
                    <div className="flex flex-wrap gap-3">
                      <button className="px-4 py-2 rounded-lg bg-surface-elevated text-text font-medium hover:bg-surface transition-colors border border-border flex items-center gap-2">
                        <Database className="w-4 h-4" />
                        Export Data
                      </button>
                      <button className="px-4 py-2 rounded-lg bg-surface-elevated text-text font-medium hover:bg-surface transition-colors border border-border flex items-center gap-2">
                        <Database className="w-4 h-4" />
                        Import Data
                      </button>
                      <button className="px-4 py-2 rounded-lg bg-error/10 text-error font-medium hover:bg-error/20 transition-colors border border-error/30 flex items-center gap-2">
                        <Trash2 className="w-4 h-4" />
                        Clear All Data
                      </button>
                    </div>
                    <p className="text-sm text-text-muted mt-2">Export/import your settings, contribution history, and preferences.</p>
                  </div>

                  <div className="pt-4 border-t border-border/50">
                    <h3 className="font-medium mb-3">About</h3>
                    <div className="space-y-2 text-sm text-text-muted">
                      <div className="flex justify-between">
                        <span>Version</span>
                        <span className="font-mono">0.1.0</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Tauri</span>
                        <span className="font-mono">2.0</span>
                      </div>
                      <div className="flex justify-between">
                        <span>BOINC Client</span>
                        <span className="font-mono">7.24.1</span>
                      </div>
                      <div className="flex justify-between">
                        <span>License</span>
                        <span className="font-mono">MIT</span>
                      </div>
                    </div>
                    <div className="flex gap-3 mt-4">
                      <a href="https://github.com/seanebones-lang/Humanity-Grid" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline text-sm">Source Code</a>
                      <a href="https://humanity-grid.org/privacy" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline text-sm">Privacy Policy</a>
                      <a href="https://humanity-grid.org/terms" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline text-sm">Terms of Service</a>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}