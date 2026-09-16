-- Initial schema for Humanity Grid Volunteer App
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE contributions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    work_unit_id TEXT NOT NULL,
    hours REAL NOT NULL,
    validated BOOLEAN DEFAULT FALSE,
    credits INTEGER DEFAULT 0,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project_stories (
    project_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    your_contribution TEXT,
    molecules_screened INTEGER DEFAULT 0,
    hours_donated REAL DEFAULT 0,
    status TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE team_members (
    team_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (team_id, user_id)
);

CREATE INDEX idx_contributions_project ON contributions(project_id);
CREATE INDEX idx_contributions_completed_at ON contributions(completed_at);