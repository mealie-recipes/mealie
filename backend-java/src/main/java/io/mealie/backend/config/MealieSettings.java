package io.mealie.backend.config;

import io.mealie.backend.db.DbEngine;
import java.nio.file.Files;
import java.nio.file.Path;
import org.springframework.core.env.Environment;

/**
 * The subset of the Python backend's settings the Java backend needs, resolved with the same rules
 * (see mealie/core/config.py and mealie/core/settings/settings.py).
 */
public record MealieSettings(boolean production, boolean testing, Path baseDir, Path dataDir, DbEngine dbEngine) {

    /** Python's non-production secret, see determine_secrets() in mealie/core/settings/settings.py. */
    public static final String NON_PRODUCTION_SECRET = "shh-secret-test-key";

    public static MealieSettings resolve(MealieEnv env, Path baseDir) {
        boolean production = env.flag("PRODUCTION", true);
        boolean testing = env.flag("TESTING", false);
        String dataDirSetting = env.get("DATA_DIR").orElse(null);

        Path dataDir;
        if (testing) {
            dataDir = baseDir.resolve(dataDirSetting != null ? dataDirSetting : "tests/.temp");
        } else if (production) {
            dataDir = Path.of(dataDirSetting != null ? dataDirSetting : "/app/data");
        } else {
            dataDir = baseDir.resolve("dev").resolve("data");
        }

        DbEngine engine = DbEngine.fromSetting(env.get("DB_ENGINE", "sqlite"));
        return new MealieSettings(production, testing, baseDir, dataDir.toAbsolutePath().normalize(), engine);
    }

    /** Same location as SQLiteProvider.db_path in mealie/core/settings/db_providers.py. */
    public Path sqlitePath() {
        return dataDir.resolve("mealie.db");
    }

    public Path secretFile() {
        return dataDir.resolve(".secret");
    }

    /**
     * The repository root, which is where the Python backend reads {@code .env} from. MEALIE_BASE_DIR wins;
     * otherwise walk up from the working directory to the checkout that contains the Python package.
     */
    public static Path detectBaseDir(Environment environment) {
        String override = environment.getProperty("MEALIE_BASE_DIR");
        if (override != null && !override.isBlank()) {
            return Path.of(override).toAbsolutePath().normalize();
        }
        Path cwd = Path.of("").toAbsolutePath();
        for (Path dir = cwd; dir != null; dir = dir.getParent()) {
            if (Files.isRegularFile(dir.resolve("pyproject.toml")) && Files.isDirectory(dir.resolve("mealie"))) {
                return dir;
            }
        }
        return cwd;
    }
}
