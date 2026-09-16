export interface SystemInfo {
  cpu_usage: number
  total_memory: number
  used_memory: number
  available_memory: number
  cpus: CpuInfo[]
  gpus: GpuInfo[]
  os: string
  arch: string
}

export interface CpuInfo {
  name: string
  usage: number
  frequency: number
}

export interface GpuInfo {
  name: string
  vendor: string
  memory_total: number
  memory_used: number
  utilization: number
  temperature: number | null
}

export interface ThermalInfo {
  temperatures: TemperatureReading[]
}

export interface TemperatureReading {
  label: string
  temperature: number
  max: number | null
  critical: number | null
}

export interface PowerInfo {
  on_battery: boolean
  battery_percentage: number
  time_remaining: number | null
  is_charging: boolean
}

export interface BoincStatus {
  running: boolean
  connected: boolean
  active_tasks: number
  gpu_tasks: number
  cpu_tasks: number
  download_speed: number
  upload_speed: number
}

export interface UserSettings {
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

export interface CauseAllocation {
  id: string
  name: string
  icon: string
  percentage: number
  enabled: boolean
}

export interface ScheduleConfig {
  weekday_start: string
  weekday_end: string
  weekend_all_day: boolean
  custom_hours: ScheduleEntry[]
}

export interface ScheduleEntry {
  day: string
  start: string
  end: string
}

export interface ContributionStats {
  total_hours: number
  validated_work_units: number
  projects_contributed: number
  papers_published: number
  current_streak: number
  total_credits: number
}

export interface ProjectStory {
  project_id: string
  title: string
  description: string
  your_contribution: string
  molecules_screened: number
  hours_donated: number
  status: string
}