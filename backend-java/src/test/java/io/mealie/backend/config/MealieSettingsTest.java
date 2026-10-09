package io.mealie.backend.config;

import static org.assertj.core.api.Assertions.assertThat;

import io.mealie.backend.db.DbEngine;
import java.nio.file.Path;
import java.util.Map;
import org.junit.jupiter.api.Test;

class MealieSettingsTest {

    private static final Path BASE = Path.of("/repo");

    private static MealieSettings resolve(Map<String, String> env) {
        return MealieSettings.resolve(new MealieEnv(env::get, Map.of()), BASE);
    }

    @Test
    void productionIsTheDefaultAndUsesAppData() {
        MealieSettings settings = resolve(Map.of());
        assertThat(settings.production()).isTrue();
        assertThat(settings.dataDir()).isEqualTo(Path.of("/app/data"));
        assertThat(settings.dbEngine()).isEqualTo(DbEngine.SQLITE);
    }

    @Test
    void productionHonoursDataDir() {
        assertThat(resolve(Map.of("DATA_DIR", "/srv/mealie")).dataDir()).isEqualTo(Path.of("/srv/mealie"));
    }

    @Test
    void developmentIgnoresDataDirAndUsesDevData() {
        MealieSettings settings = resolve(Map.of("PRODUCTION", "false", "DATA_DIR", "/srv/mealie"));
        assertThat(settings.dataDir()).isEqualTo(Path.of("/repo/dev/data"));
        assertThat(settings.sqlitePath()).isEqualTo(Path.of("/repo/dev/data/mealie.db"));
    }

    @Test
    void testingResolvesDataDirAgainstBaseDir() {
        assertThat(resolve(Map.of("TESTING", "1")).dataDir()).isEqualTo(Path.of("/repo/tests/.temp"));
        assertThat(resolve(Map.of("TESTING", "true", "DATA_DIR", "x")).dataDir()).isEqualTo(Path.of("/repo/x"));
    }

    @Test
    void onlyTheExactValuePostgresSelectsPostgres() {
        assertThat(resolve(Map.of("DB_ENGINE", "postgres")).dbEngine()).isEqualTo(DbEngine.POSTGRES);
        assertThat(resolve(Map.of("DB_ENGINE", "Postgres")).dbEngine()).isEqualTo(DbEngine.SQLITE);
        assertThat(resolve(Map.of("DB_ENGINE", "anything")).dbEngine()).isEqualTo(DbEngine.SQLITE);
    }

    @Test
    void processEnvironmentWinsOverDotenv() {
        MealieEnv env = new MealieEnv(Map.of("DB_ENGINE", "sqlite")::get,
                Map.of("DB_ENGINE", "postgres", "POSTGRES_DB", "fromfile"));
        assertThat(env.get("DB_ENGINE")).contains("sqlite");
        assertThat(env.get("POSTGRES_DB")).contains("fromfile");
    }
}
