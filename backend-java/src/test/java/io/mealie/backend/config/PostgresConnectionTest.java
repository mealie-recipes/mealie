package io.mealie.backend.config;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.Map;
import org.junit.jupiter.api.Test;

class PostgresConnectionTest {

    private static PostgresConnection fromEnv(Map<String, String> env) {
        return PostgresConnection.fromEnv(new MealieEnv(env::get, Map.of()));
    }

    @Test
    void defaultsMatchThePythonProvider() {
        PostgresConnection pg = fromEnv(Map.of());
        assertThat(pg.jdbcUrl()).startsWith("jdbc:postgresql://postgres:5432/mealie?");
        assertThat(pg.username()).isEqualTo("mealie");
        assertThat(pg.password()).isEqualTo("mealie");
    }

    @Test
    void buildsFromIndividualVariables() {
        PostgresConnection pg = fromEnv(Map.of(
                "POSTGRES_SERVER", "db.local", "POSTGRES_PORT", "6543", "POSTGRES_DB", "recipes",
                "POSTGRES_USER", "chef", "POSTGRES_PASSWORD", "p@ss:w/rd${x}"));
        assertThat(pg.jdbcUrl()).isEqualTo("jdbc:postgresql://db.local:6543/recipes?" + PostgresConnection.JDBC_PARAMS);
        assertThat(pg.username()).isEqualTo("chef");
        assertThat(pg.password()).isEqualTo("p@ss:w/rd${x}");
    }

    @Test
    void stringParametersAreSentUntypedSoEnumsAndJsonBind() {
        assertThat(fromEnv(Map.of()).jdbcUrl()).contains("stringtype=unspecified");
    }

    @Test
    void overrideWinsAndKeepsPasswordLiteral() {
        PostgresConnection pg = fromEnv(Map.of(
                "POSTGRES_SERVER", "ignored",
                "POSTGRES_URL_OVERRIDE", "postgresql://chef:p@ss:w0rd@db.example.com:5432/mealie?sslmode=require"));
        assertThat(pg.jdbcUrl())
                .isEqualTo("jdbc:postgresql://db.example.com:5432/mealie?sslmode=require&" + PostgresConnection.JDBC_PARAMS);
        assertThat(pg.username()).isEqualTo("chef");
        assertThat(pg.password()).isEqualTo("p@ss:w0rd");
    }

    @Test
    void overrideWithoutCredentials() {
        PostgresConnection pg = PostgresConnection.fromUrl("postgresql://db:5432/mealie");
        assertThat(pg.jdbcUrl()).isEqualTo("jdbc:postgresql://db:5432/mealie?" + PostgresConnection.JDBC_PARAMS);
        assertThat(pg.username()).isNull();
    }

    @Test
    void overrideMustBePostgresql() {
        assertThatThrownBy(() -> PostgresConnection.fromUrl("postgres://db/mealie"))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void toStringHidesPassword() {
        assertThat(fromEnv(Map.of("POSTGRES_PASSWORD", "hunter2")).toString()).doesNotContain("hunter2");
    }
}
