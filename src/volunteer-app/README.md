# Humanity Grid volunteer interface design preview

This browser interface lets contributors review planned cause allocation and resource preferences. It does not dispatch computation, monitor hardware, connect to BOINC, create accounts, claim contributions, or enforce thermal/resource limits. Preview changes live in React state and reset on reload. No native privileges are requested by the browser preview.

## Run the supported preview

Use Node 22.12+ or 24+ and npm:

```bash
cd src/volunteer-app
npm ci --ignore-scripts
npm run build
npm run preview -- --port 4365
```

Open the loopback URL printed by Vite. To develop, use `npm run dev`.

The production web build and locked dependency audit are checked in CI. Browser reviews must verify the status banner, navigation, cause allocation, resource controls, empty contributions/teams, and reload behavior before release.

## Native wrapper: unsupported scaffold

`src-tauri` is an incomplete development scaffold, not a signed or verified installer. Its command handlers, plugin dependencies, permissions, hardware behavior, and BOINC adapter need a separate implementation and platform test effort. Do not distribute it, run `tauri:build` as an installation path, or advertise volunteer execution as available. A working web preview does not validate the native wrapper.

## Path to an actual volunteer release

Authenticated dispatch and submission; verified input/container provenance; bounded CPU/GPU/thermal/power enforcement; independently rerun scientific validation; visible result coverage; secure update and signed platform installers; accessibility and recovery testing. The local Proof A reviewer tools are available now; see the repository root and `docs/PROOF_A_REVIEW.md`.
