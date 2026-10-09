package io.mealie.backend.config;

import static org.assertj.core.api.Assertions.assertThat;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class MealieEnvTest {

    @Test
    void parsesDotenvLikePythonDotenv(@TempDir Path dir) throws Exception {
        Path file = dir.resolve(".env");
        Files.writeString(file, """
                # comment
                DB_ENGINE=postgres
                export POSTGRES_USER=chef
                POSTGRES_PASSWORD="quoted # not a comment"
                POSTGRES_DB=mealie # trailing comment
                EMPTY=
                not a pair
                """);
        Map<String, String> values = MealieEnv.readDotenv(file);
        assertThat(values).containsEntry("DB_ENGINE", "postgres")
                .containsEntry("POSTGRES_USER", "chef")
                .containsEntry("POSTGRES_PASSWORD", "quoted # not a comment")
                .containsEntry("POSTGRES_DB", "mealie")
                .containsEntry("EMPTY", "")
                .hasSize(5);
    }

    @Test
    void missingDotenvIsEmpty(@TempDir Path dir) {
        assertThat(MealieEnv.readDotenv(dir.resolve(".env"))).isEmpty();
    }

    @Test
    void flagsAcceptTrueAndOneOnly() {
        MealieEnv env = new MealieEnv(Map.of("A", "TRUE", "B", "1", "C", "yes")::get, Map.of());
        assertThat(env.flag("A", false)).isTrue();
        assertThat(env.flag("B", false)).isTrue();
        assertThat(env.flag("C", true)).isFalse();
        assertThat(env.flag("MISSING", true)).isTrue();
    }
}
