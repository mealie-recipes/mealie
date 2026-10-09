package io.mealie.backend.db;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import io.mealie.backend.config.MealieSettings;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfSystemProperty;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;

/**
 * Checks the dialect against rows the Python backend actually wrote, on whichever engine the environment selects
 * ({@code task java:test:db ENGINE=sqlite|postgres}). Read-only: every value is read through the dialect, then bound
 * back through the dialect in a WHERE clause, which only matches if Java writes exactly what Python stores.
 */
@SpringBootTest
@EnabledIfSystemProperty(named = "mealie.dbtest", matches = "true")
class SharedSchemaCompatibilityTest {

    @Autowired
    NamedParameterJdbcTemplate jdbc;

    @Autowired
    SqlDialect dialect;

    @Autowired
    MealieSettings settings;

    record UserRow(UUID id, Boolean admin, OffsetDateTime createdAt, String authMethod) {
    }

    private List<UserRow> users() {
        List<UserRow> rows = jdbc.query("SELECT id, admin, created_at, auth_method FROM users", (rs, i) -> new UserRow(
                dialect.getUuid(rs, "id"), dialect.getBool(rs, "admin"), dialect.getTimestamp(rs, "created_at"),
                rs.getString("auth_method")));
        assumeTrue(!rows.isEmpty(), "no users yet; start the Python backend once so it seeds the database");
        return rows;
    }

    @Test
    void engineMatchesTheEnvironment() {
        String expected = System.getenv().getOrDefault("DB_ENGINE", "sqlite");
        assertThat(dialect.engine()).isEqualTo(DbEngine.fromSetting(expected));
        assertThat(settings.dbEngine()).isEqualTo(dialect.engine());
    }

    @Test
    void schemaIsMigratedByAlembic() {
        assertThat(jdbc.getJdbcTemplate().queryForList("SELECT version_num FROM alembic_version", String.class))
                .hasSize(1);
    }

    @Test
    void uuidBooleanAndDatetimeParametersMatchPythonRows() {
        for (UserRow user : users()) {
            MapSqlParameterSource params = new MapSqlParameterSource()
                    .addValue("id", dialect.uuid(user.id()))
                    .addValue("admin", dialect.bool(user.admin()))
                    .addValue("createdAt", dialect.timestamp(user.createdAt()));
            Integer count = jdbc.queryForObject(
                    "SELECT COUNT(*) FROM users WHERE id = :id AND admin = :admin AND created_at = :createdAt",
                    params, Integer.class);
            assertThat(count).as("user %s", user.id()).isEqualTo(1);
        }
    }

    @Test
    void datetimeOrderingWorksAsAComparison() {
        UserRow first = users().getFirst();
        Integer count = jdbc.queryForObject(
                "SELECT COUNT(*) FROM users WHERE id = :id AND created_at >= :from AND created_at < :to",
                new MapSqlParameterSource()
                        .addValue("id", dialect.uuid(first.id()))
                        .addValue("from", dialect.timestamp(first.createdAt()))
                        .addValue("to", dialect.timestamp(first.createdAt().plusNanos(1_000))),
                Integer.class);
        assertThat(count).isEqualTo(1);
    }

    @Test
    void foreignKeyUuidsJoin() {
        Integer joined = jdbc.getJdbcTemplate().queryForObject(
                "SELECT COUNT(*) FROM users u JOIN groups g ON g.id = u.group_id", Integer.class);
        Integer total = jdbc.getJdbcTemplate().queryForObject("SELECT COUNT(*) FROM users", Integer.class);
        assertThat(joined).isEqualTo(total);
    }

    @Test
    void stringParameterBindsToEnumColumn() {
        // users.auth_method is a native enum on Postgres; a String parameter must still compare.
        UserRow user = users().getFirst();
        Integer count = jdbc.queryForObject("SELECT COUNT(*) FROM users WHERE id = :id AND auth_method = :method",
                new MapSqlParameterSource()
                        .addValue("id", dialect.uuid(user.id()))
                        .addValue("method", user.authMethod()),
                Integer.class);
        assertThat(count).isEqualTo(1);
    }

    @Test
    void dateParametersMatchPythonRows() {
        List<LocalDate> dates = jdbc.query("SELECT date FROM group_meal_plans",
                (rs, i) -> dialect.getDate(rs, "date"));
        assumeTrue(!dates.isEmpty(), "no meal plans to check dates against");
        for (LocalDate date : dates) {
            Integer count = jdbc.queryForObject("SELECT COUNT(*) FROM group_meal_plans WHERE date = :date",
                    new MapSqlParameterSource("date", dialect.date(date)), Integer.class);
            assertThat(count).as("meal plan date %s", date).isPositive();
        }
    }
}
