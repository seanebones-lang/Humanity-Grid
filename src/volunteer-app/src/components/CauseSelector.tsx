import { useState } from 'react'
import { Slider, Checkbox } from '@/components/ui'
import { Dna, Brain, Bug, Globe, Zap, FlaskConical } from 'lucide-react'
import { UserSettings, CauseAllocation } from '@/types'

interface CauseSelectorProps {
  settings: UserSettings | null
  onUpdate: (settings: UserSettings) => void
}

const CAUSES: {id: string; name: string; icon: React.ReactNode}[] = [
  { id: 'cancer', name: 'Cancer Research', icon: <Dna className="w-5 h-5" /> },
  { id: 'alzheimer', name: "Alzheimer's Research", icon: <Brain className="w-5 h-5" /> },
  { id: 'antibiotics', name: 'Antibiotic Discovery', icon: <Bug className="w-5 h-5" /> },
  { id: 'climate', name: 'Climate Modeling', icon: <Globe className="w-5 h-5" /> },
  { id: 'energy', name: 'Clean Energy Materials', icon: <Zap className="w-5 h-5" /> },
  { id: 'rare', name: 'Rare Diseases', icon: <FlaskConical className="w-5 h-5" /> },
]

export default function CauseSelector({ settings, onUpdate }: CauseSelectorProps) {
  const [causes, setCauses] = useState<CauseAllocation[]>((settings?.causes.length ? settings.causes : CAUSES.map(c => ({ id: c.id, name: c.name, icon: c.id, percentage: 0, enabled: false }))))

  const totalPercentage = causes.reduce((sum, c) => sum + (c.enabled ? c.percentage : 0), 0)

  const handlePercentageChange = (id: string, percentage: number) => {
    const newCauses = causes.map(c => c.id === id ? { ...c, percentage } : c)
    setCauses(newCauses)
    if (settings) onUpdate({ ...settings, causes: newCauses })
  }

  const handleEnabledChange = (id: string, enabled: boolean) => {
    const newCauses = causes.map(c => c.id === id ? { ...c, enabled } : c)
    setCauses(newCauses)
    if (settings) onUpdate({ ...settings, causes: newCauses })
  }

  const normalizePercentages = () => {
    const enabledCauses = causes.filter(c => c.enabled)
    if (enabledCauses.length === 0) return
    const perCause = Math.floor(100 / enabledCauses.length)
    const remainder = 100 % enabledCauses.length
    let enabledIndex = 0
    const newCauses = causes.map(c => {
      if (!c.enabled) return { ...c, percentage: 0 }
      return { ...c, percentage: perCause + (enabledIndex++ < remainder ? 1 : 0) }
    })
    setCauses(newCauses)
    if (settings) onUpdate({ ...settings, causes: newCauses })
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold mb-2">Preview your preferred research causes</h1>
        <p className="text-text-muted">Choose the research areas you want to support. Drag to allocate your compute percentage.</p>
      </div>

      <div className="glass rounded-xl p-6 space-y-4">
        {CAUSES.map((cause) => {
          const causeData = causes.find(c => c.id === cause.id) || { percentage: 0, enabled: false }
          return (
            <div key={cause.id} className="flex items-center gap-4 p-4 rounded-lg bg-surface/50 border border-border/50">
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10 text-primary">
                {cause.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium truncate">{cause.name}</h3>
                  <Checkbox
                    aria-label={"Enable " + cause.name} checked={causeData.enabled}
                    onCheckedChange={checked => handleEnabledChange(cause.id, checked)}
                    className="data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                  />
                </div>
                {causeData.enabled && (
                  <div className="mt-2 space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-text-muted">Compute allocation</span>
                      <span className="font-mono font-medium">{causeData.percentage}%</span>
                    </div>
                    <Slider
                      aria-label={cause.name + " preview allocation"} value={[causeData.percentage]}
                      onValueChange={([value]) => handlePercentageChange(cause.id, value)}
                      max={100}
                      step={1}
                      disabled={!causeData.enabled}
                      className="h-2"
                    />
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <div className="glass rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Total Allocation</h3>
          <span className={"font-mono text-lg " + (totalPercentage === 100 ? 'text-success' : totalPercentage > 100 ? 'text-error' : 'text-warning')}>
            {totalPercentage}%
          </span>
        </div>
        <div className="h-3 bg-surface rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary to-primary-light rounded-full transition-all duration-300"
            style={{ width: `${Math.min(totalPercentage, 100)}%` }}
          />
        </div>
        {totalPercentage !== 100 && (
          <p className="mt-2 text-sm text-text-muted">
            {totalPercentage < 100 ? `${100 - totalPercentage}% unallocated` : `${totalPercentage - 100}% overallocated`}
          </p>
        )}
        {totalPercentage > 0 && totalPercentage !== 100 && (
          <button
            onClick={normalizePercentages}
            className="mt-4 w-full sm:w-auto px-4 py-2 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 text-sm font-medium transition-colors"
          >
            Auto-balance ({Math.floor(100 / causes.filter(c => c.enabled).length)}% each)
          </button>
        )}
      </div>

      <p className="text-text-muted">Planned cause preferences only. No research project or volunteer server is connected.</p>
    </div>
  )
}
