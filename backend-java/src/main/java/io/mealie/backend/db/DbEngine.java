package io.mealie.backend.db;

public enum DbEngine {
    SQLITE("sqlite"),
    POSTGRES("postgres");

    private final String settingValue;

    DbEngine(String settingValue) {
        this.settingValue = settingValue;
    }

    /** The value used in DB_ENGINE and reported by the Python backend's /api/admin/about as dbType. */
    public String settingValue() {
        return settingValue;
    }

    /** Matches db_provider_factory(): exactly "postgres" selects Postgres, anything else is SQLite. */
    public static DbEngine fromSetting(String value) {
        return "postgres".equals(value) ? POSTGRES : SQLITE;
    }
}
