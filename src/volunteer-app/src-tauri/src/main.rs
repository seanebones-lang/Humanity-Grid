#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_websocket::init())
        .plugin(tauri_plugin_sql::Builder::default().add_migrations("sqlite:humanity_grid.db", vec![
            tauri_plugin_sql::Migration {
                version: 1,
                description: "create_initial_tables",
                sql: include_str!("../migrations/001_initial.sql"),
                kind: tauri_plugin_sql::MigrationKind::Up,
            }
        ]).build())
        .setup(|app| {
            // Initialize system monitoring
            #[cfg(debug_assertions)]
            {
                let window = app.get_webview_window("main").unwrap();
                window.open_devtools();
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // System info
            get_system_info,
            get_thermal_info,
            get_power_info,
            // BOINC control
            boinc_get_status,
            boinc_start,
            boinc_stop,
            boinc_pause,
            boinc_resume,
            // Settings
            get_settings,
            update_settings,
            // Contributions
            get_contributions,
            get_project_stories,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

// System info commands
#[tauri::command]
async fn get_system_info() -> Result<SystemInfo, String> {
    let mut sys = sysinfo::System::new_all();
    sys.refresh_all();

    let cpu_usage = sys.global_cpu_usage();
    let total_memory = sys.total_memory();
    let used_memory = sys.used_memory();
    let available_memory = sys.available_memory();

    let cpus = sys.cpus().iter().map(|cpu| CpuInfo {
        name: cpu.name().to_string(),
        usage: cpu.cpu_usage(),
        frequency: cpu.frequency(),
    }).collect();

    let gpus = detect_gpus();

    Ok(SystemInfo {
        cpu_usage,
        total_memory,
        used_memory,
        available_memory,
        cpus,
        gpus,
        os: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
    })
}

#[tauri::command]
async fn get_thermal_info() -> Result<ThermalInfo, String> {
    let mut sys = sysinfo::System::new_all();
    sys.refresh_all();

    let temperatures = sys.components().iter().map(|comp| TemperatureReading {
        label: comp.label().to_string(),
        temperature: comp.temperature(),
        max: comp.max(),
        critical: comp.critical(),
    }).collect();

    Ok(ThermalInfo { temperatures })
}

#[tauri::command]
async fn get_power_info() -> Result<PowerInfo, String> {
    // Platform-specific power detection
    // For now, return mock data
    Ok(PowerInfo {
        on_battery: false,
        battery_percentage: 100,
        time_remaining: None,
        is_charging: true,
    })
}

// BOINC commands (stubs - will implement full integration)
#[tauri::command]
async fn boinc_get_status() -> Result<BoincStatus, String> {
    Ok(BoincStatus {
        running: false,
        connected: false,
        active_tasks: 0,
        gpu_tasks: 0,
        cpu_tasks: 0,
        download_speed: 0.0,
        upload_speed: 0.0,
    })
}

#[tauri::command]
async fn boinc_start() -> Result<(), String> {
    // TODO: Start BOINC client
    Ok(())
}

#[tauri::command]
async fn boinc_stop() -> Result<(), String> {
    // TODO: Stop BOINC client
    Ok(())
}

#[tauri::command]
async fn boinc_pause() -> Result<(), String> {
    Ok(())
}

#[tauri::command]
async fn boinc_resume() -> Result<(), String> {
    Ok(())
}

// Settings commands
#[tauri::command]
async fn get_settings() -> Result<UserSettings, String> {
    // TODO: Load from database
    Ok(UserSettings::default())
}

#[tauri::command]
async fn update_settings(settings: UserSettings) -> Result<(), String> {
    // TODO: Save to database
    Ok(())
}

// Contributions commands
#[tauri::command]
async fn get_contributions() -> Result<ContributionStats, String> {
    Ok(ContributionStats {
        total_hours: 0.0,
        validated_work_units: 0,
        projects_contributed: 0,
        papers_published: 0,
        current_streak: 0,
        total_credits: 0,
    })
}

#[tauri::command]
async fn get_project_stories() -> Result<Vec<ProjectStory>, String> {
    Ok(vec![])
}

// Data structures
#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
struct SystemInfo {
    cpu_usage: f32,
    total_memory: u64,
    used_memory: u64,
    available_memory: u64,
    cpus: Vec<CpuInfo>,
    gpus: Vec<GpuInfo>,
    os: String,
    arch: String,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
struct CpuInfo {
    name: String,
    usage: f32,
    frequency: u64,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
struct GpuInfo {
    name: String,
    vendor: String,
    memory_total: u64,
    memory_used: u64,
    utilization: f32,
    temperature: Option<f32>,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
struct ThermalInfo {
    temperatures: Vec<TemperatureReading>,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
struct TemperatureReading {
    label: String,
    temperature: f32,
    max: Option<f32>,
    critical: Option<f32>,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
struct PowerInfo {
    on_battery: bool,
    battery_percentage: u8,
    time_remaining: Option<u64>,
    is_charging: bool,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
struct BoincStatus {
    running: bool,
    connected: bool,
    active_tasks: u32,
    gpu_tasks: u32,
    cpu_tasks: u32,
    download_speed: f64,
    upload_speed: f64,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug, Default)]
struct UserSettings {
    causes: Vec<CauseAllocation>,
    cpu_limit_percent: u8,
    gpu_limit_percent: u8,
    memory_limit_gb: u32,
    thermal_limit_celsius: u8,
    thermal_resume_celsius: u8,
    run_on_battery: bool,
    schedule: ScheduleConfig,
    network_wifi_only: bool,
    network_metered_allowed: bool,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
struct CauseAllocation {
    id: String,
    name: String,
    icon: String,
    percentage: u8,
    enabled: bool,
}

impl Default for UserSettings {
    fn default() -> Self {
        Self {
            causes: vec![
                CauseAllocation { id: "cancer".into(), name: "Cancer Research".into(), icon: "🧬".into(), percentage: 50, enabled: true },
                CauseAllocation { id: "alzheimer".into(), name: "Alzheimer's Research".into(), icon: "🧠".into(), percentage: 30, enabled: true },
                CauseAllocation { id: "antibiotics".into(), name: "Antibiotic Discovery".into(), icon: "🦠".into(), percentage: 20, enabled: true },
                CauseAllocation { id: "climate".into(), name: "Climate Modeling".into(), icon: "🌎".into(), percentage: 0, enabled: false },
                CauseAllocation { id: "energy".into(), name: "Clean Energy".into(), icon: "🔋".into(), percentage: 0, enabled: false },
                CauseAllocation { id: "rare".into(), name: "Rare Diseases".into(), icon: "🧬".into(), percentage: 0, enabled: false },
            ],
            cpu_limit_percent: 30,
            gpu_limit_percent: 40,
            memory_limit_gb: 8,
            thermal_limit_celsius: 75,
            thermal_resume_celsius: 65,
            run_on_battery: false,
            schedule: ScheduleConfig::default(),
            network_wifi_only: true,
            network_metered_allowed: false,
        }
    }
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug, Default)]
struct ScheduleConfig {
    weekday_start: String,
    weekday_end: String,
    weekend_all_day: bool,
    custom_hours: Vec<ScheduleEntry>,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
struct ScheduleEntry {
    day: String,
    start: String,
    end: String,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
struct ContributionStats {
    total_hours: f64,
    validated_work_units: u64,
    projects_contributed: u32,
    papers_published: u32,
    current_streak: u32,
    total_credits: u64,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
struct ProjectStory {
    project_id: String,
    title: String,
    description: String,
    your_contribution: String,
    molecules_screened: u64,
    hours_donated: f64,
    status: String,
}

fn detect_gpus() -> Vec<GpuInfo> {
    // Platform-specific GPU detection
    // For now, return empty - will implement with platform-specific code
    vec![]
}