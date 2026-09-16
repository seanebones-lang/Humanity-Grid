# Volunteer App

**Cross-platform desktop application for volunteers to donate compute to Humanity Grid.**

Built with **Tauri 2** (Rust + Web frontend) for native performance, small binary size, and beautiful UI.

## Features

- **Cause Selection**: Choose which research areas to support (cancer, Alzheimer's, antibiotics, climate, clean energy, rare diseases)
- **Resource Controls**: CPU/GPU percentage limits, core count, memory limits
- **Thermal Management**: Pause above temperature threshold, resume when cool
- **Power Awareness**: Battery detection, scheduled run hours, electricity cost optimization
- **Contribution Dashboard**: Real-time stats, validated work units, project impact
- **Project Stories**: Human-readable descriptions of what your computer achieved
- **Team/Organization Support**: Join teams, compete on leaderboards
- **Offline-First**: Queue work units, sync when online
- **Zero-Trust Security**: Sandboxed execution, no filesystem/network access beyond work units

## Architecture

```
volunteer-app/
├── src-tauri/                 # Rust backend
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   ├── src/
│   │   ├── main.rs
│   │   ├── boinc/             # BOINC client integration
│   │   ├── system/            # Hardware detection, thermal, power
│   │   ├── scheduler/         # Work scheduling, resource limits
│   │   ├── sandbox/           # Process isolation, security
│   │   ├── api/               # Humanity Grid API client
│   │   ├── storage/           # Local SQLite for offline queue
│   │   └── notifications/     # System notifications
│   ├── build.rs
│   └── icons/
├── src/                       # Frontend (React + TypeScript + Tailwind)
│   ├── main.tsx
│   ├── App.tsx
│   ├── components/
│   │   ├── CauseSelector.tsx
│   │   ├── ResourceControls.tsx
│   │   ├── ThermalMonitor.tsx
│   │   ├── PowerSchedule.tsx
│   │   ├── Dashboard.tsx
│   │   ├── ProjectStories.tsx
│   │   ├── TeamLeaderboard.tsx
│   │   └── Settings.tsx
│   ├── hooks/
│   │   ├── useBoinc.ts
│   │   ├── useSystemInfo.ts
│   │   └── useContributions.ts
│   ├── services/
│   │   ├── api.ts
│   │   └── storage.ts
│   ├── types/
│   │   └── index.ts
│   └── styles/
│       └── globals.css
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── vite.config.ts
└── index.html
```

## Technology Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| Backend | Rust (Tauri 2) | Native performance, memory safety, small binary |
| Frontend | React 19 + TypeScript | Modern, type-safe, component-based |
| Styling | Tailwind 4 | Utility-first, small bundle, dark mode |
| Build | Vite 6 | Fast dev, optimized production builds |
| Database | SQLite (sqlx) | Embedded, offline-capable, ACID |
| BOINC | boinc-client lib / CLI | Proven volunteer computing client |
| Hardware | sysinfo, hwmon | Cross-platform system monitoring |
| Sandbox | firejail / seccomp / App Sandbox | Process isolation |

## Resource Control Model

```
User Settings
├── Causes: [cancer: 50%, alzheimer: 30%, antibiotics: 20%]
├── CPU: max 30% (4 of 12 cores)
├── GPU: max 40% (time-sliced)
├── Memory: max 8 GB
├── Thermal: pause at 75°C, resume at 65°C
├── Battery: pause on battery, resume on AC
├── Schedule: 22:00-07:00 weekdays, all day weekends
└── Network: only on WiFi, not metered
```

## Security Model

```
Volunteer App (Tauri)
    │
    ├─► BOINC Client (separate process, user-level)
    │       │
    │       └─► Slot Directory (per work unit)
    │               ├─► Input files (read-only)
    │               ├─► Output files (write)
    │               └─► Docker container (if Docker workload)
    │
    └─► Sandbox Enforcement
            ├─► CPU affinity / cgroups
            ├─► Memory limits (cgroups / job objects)
            ├─► GPU time-slicing (CUDA MPS / ROCm)
            ├─► Network: DENY (except BOINC scheduler RPC)
            ├─► Filesystem: DENY (except slot directory)
            ├─► Thermal monitoring (poll hwmon / SMC)
            └─► Power monitoring (UPower / Windows API / macOS IOPM)
```

## UI Mockup (Text)

```
┌─────────────────────────────────────────────────────────────┐
│  Humanity Grid                          [⚙] [👤] [❌]        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  What do you want your computer working on tonight?         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🧬 Cancer Research              ████████████░░ 50%  │   │
│  │ 🧠 Alzheimer's Research         ██████░░░░░░░░ 30%  │   │
│  │ 🦠 Antibiotic Discovery         ████░░░░░░░░░░ 20%  │   │
│  │ 🌎 Climate Modeling             ░░░░░░░░░░░░░░  0%  │   │
│  │ 🔋 Clean Energy Materials       ░░░░░░░░░░░░░░  0%  │   │
│  │ 🧬 Rare Diseases                ░░░░░░░░░░░░░░  0%  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐  │
│  │ Use my computer │  │ Maximum CPU     │  │ Maximum GPU │  │
│  │ [While idle ▼]  │  │ [30%] ████░░░░░░ │  │ [40%] ██████░░ │
│  └─────────────────┘  └─────────────────┘  └────────────┘  │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐  │
│  │ Run on battery  │  │ Pause above     │  │ Schedule   │  │
│  │ [No ▼]          │  │ [75°C] ███████░ │  │ [Nights ▼] │  │
│  └─────────────────┘  └─────────────────┘  └────────────┘  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Tonight your computer screened 18,421 molecules           │
│  for a pediatric cancer study.  🎗                          │
│                                                             │
│  [Pause]                    [View Details →]               │
└─────────────────────────────────────────────────────────────┘
```

## Development Setup

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install Node.js (via fnm/nvm/volta)
fnm install 22

# Install Tauri CLI
cargo install tauri-cli

# Install frontend dependencies
cd src/volunteer-app
npm install

# Run in development
npm run tauri dev

# Build for production
npm run tauri build
```

## Platform-Specific Notes

### macOS
- Use `sysinfo` for CPU/thermal (via `powermetrics` / `istats`)
- App Sandbox entitlements for BOINC client
- Notifications via `UNUserNotificationCenter`
- Code signing required for distribution

### Windows
- Use `sysinfo` + `wmi` for hardware info
- Thermal via `OpenHardwareMonitor` WMI or `OHM`
- BOINC installs as service
- MSI installer with WiX

### Linux
- `sysinfo` + `/sys/class/thermal` + `hwmon`
- BOINC client from package manager or AppImage
- systemd user service for background operation
- AppImage / Flatpak / Snap for distribution

## Quick Start

```bash
cd src/volunteer-app
npm install
npm run tauri dev
```

## Build Targets

| Platform | Target | Output |
|----------|--------|--------|
| macOS (Intel) | `x86_64-apple-darwin` | `.dmg`, `.app` |
| macOS (Apple Silicon) | `aarch64-apple-darwin` | `.dmg`, `.app` |
| Windows | `x86_64-pc-windows-msvc` | `.msi`, `.exe` |
| Linux | `x86_64-unknown-linux-gnu` | `.AppImage`, `.deb`, `.rpm` |