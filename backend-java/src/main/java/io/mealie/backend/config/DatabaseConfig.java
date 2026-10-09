package io.mealie.backend.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import io.mealie.backend.db.SqlDialect;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.core.env.Environment;
import org.sqlite.SQLiteConfig;
import org.sqlite.SQLiteDataSource;
import org.sqlite.SQLiteOpenMode;

/**
 * Connects to whichever database the Python backend is configured for. The schema belongs to Python/Alembic: nothing
 * here creates or migrates tables, and SQLite is opened without the CREATE flag so a missing file is an error rather
 * than a new empty database.
 */
@Configuration(proxyBeanMethods = false)
public class DatabaseConfig {

    private static final Logger log = LoggerFactory.getLogger(DatabaseConfig.class);

    /** Python's sqlite3 module waits 5 s for a lock by default; wait as long so both backends behave alike. */
    private static final int SQLITE_BUSY_TIMEOUT_MS = 5000;

    @Bean
    MealieEnv mealieEnv(ConfigurableEnvironment environment) {
        return MealieEnv.fromSpring(environment, MealieSettings.detectBaseDir(environment));
    }

    @Bean
    MealieSettings mealieSettings(MealieEnv env, Environment environment) {
        MealieSettings settings = MealieSettings.resolve(env, MealieSettings.detectBaseDir(environment));
        log.info("DB engine: {}, data dir: {}, production: {}",
                settings.dbEngine().settingValue(), settings.dataDir(), settings.production());
        return settings;
    }

    @Bean
    SqlDialect sqlDialect(MealieSettings settings) {
        return SqlDialect.forEngine(settings.dbEngine());
    }

    @Bean(destroyMethod = "close")
    DataSource dataSource(MealieSettings settings, MealieEnv env) {
        HikariConfig hikari = new HikariConfig();
        hikari.setPoolName("mealie-" + settings.dbEngine().settingValue());
        // Start even if the database isn't there yet (e.g. Python hasn't run its migrations); /api/java/health
        // reports the problem instead.
        hikari.setInitializationFailTimeout(-1);

        switch (settings.dbEngine()) {
            case SQLITE -> {
                SQLiteConfig config = new SQLiteConfig();
                config.resetOpenMode(SQLiteOpenMode.CREATE);
                config.setBusyTimeout(SQLITE_BUSY_TIMEOUT_MS);
                SQLiteDataSource sqlite = new SQLiteDataSource(config);
                sqlite.setUrl("jdbc:sqlite:" + settings.sqlitePath());
                hikari.setDataSource(sqlite);
                hikari.setMaximumPoolSize(4);
                log.info("SQLite database: {}", settings.sqlitePath());
            }
            case POSTGRES -> {
                PostgresConnection pg = PostgresConnection.fromEnv(env);
                hikari.setJdbcUrl(pg.jdbcUrl());
                hikari.setUsername(pg.username());
                hikari.setPassword(pg.password());
                hikari.setMaximumPoolSize(10);
                log.info("Postgres database: {}", pg.jdbcUrl());
            }
        }
        return new HikariDataSource(hikari);
    }
}
