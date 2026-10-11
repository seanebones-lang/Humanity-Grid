import type { UserSettings } from '@/types'
interface Props { settings: UserSettings | null; onUpdate: (settings: UserSettings) => void }
export default function SettingsPanel({ settings }: Props) {
  if (!settings) return <p>No preview preferences available.</p>
  return <section className="space-y-6"><h1 className="text-2xl font-bold">Preview preferences</h1>
    <p>Change allocations in Causes and limits in Resources. They remain in this page session and reset on reload. No account, machine settings, notification subscriptions, or native permissions are changed.</p>
    <dl className="grid grid-cols-2 gap-4 p-6 bg-surface rounded-xl">
      <dt>CPU preference</dt><dd>{settings.cpu_limit_percent}%</dd>
      <dt>GPU preference</dt><dd>{settings.gpu_limit_percent}%</dd>
      <dt>RAM preference</dt><dd>{settings.memory_limit_gb} GB</dd>
      <dt>Pause threshold preference</dt><dd>{settings.thermal_limit_celsius}°C</dd>
      <dt>Selected causes</dt><dd>{settings.causes.filter(c => c.enabled).length}</dd>
    </dl>
    <p className="text-text-muted">Native preferences and authenticated volunteer execution require a future implementation and platform checks.</p>
  </section>
}
