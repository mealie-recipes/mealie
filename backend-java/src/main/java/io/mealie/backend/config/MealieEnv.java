package io.mealie.backend.config;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.core.env.PropertySource;

/**
 * Environment lookup with the same precedence as the Python backend: process environment first, then the
 * repository's {@code .env} file (python-dotenv / pydantic-settings never override variables that are already set).
 */
public final class MealieEnv {

    private final Function<String, String> process;
    private final Map<String, String> dotenv;

    public MealieEnv(Function<String, String> process, Map<String, String> dotenv) {
        this.process = process;
        this.dotenv = Map.copyOf(dotenv);
    }

    /**
     * Spring's Environment covers the process environment, and lets tests supply values as properties. Values are
     * read raw from the property sources: Environment.getProperty() would expand "${...}" inside them, which would
     * corrupt e.g. a password that contains those characters.
     */
    public static MealieEnv fromSpring(ConfigurableEnvironment environment, Path baseDir) {
        return new MealieEnv(key -> rawProperty(environment, key), readDotenv(baseDir.resolve(".env")));
    }

    private static String rawProperty(ConfigurableEnvironment environment, String key) {
        for (PropertySource<?> source : environment.getPropertySources()) {
            Object value = source.getProperty(key);
            if (value != null) {
                return value.toString();
            }
        }
        return null;
    }

    public Optional<String> get(String key) {
        String value = process.apply(key);
        if (value == null) {
            value = dotenv.get(key);
        }
        return Optional.ofNullable(value);
    }

    public String get(String key, String fallback) {
        return get(key).orElse(fallback);
    }

    /** Mirrors {@code os.getenv(key, default).lower() in ["true", "1"]} in mealie/core/config.py. */
    public boolean flag(String key, boolean fallback) {
        String value = get(key, fallback ? "True" : "False").toLowerCase();
        return value.equals("true") || value.equals("1");
    }

    static Map<String, String> readDotenv(Path file) {
        Map<String, String> values = new HashMap<>();
        if (!Files.isRegularFile(file)) {
            return values;
        }
        try {
            for (String raw : Files.readAllLines(file, StandardCharsets.UTF_8)) {
                String line = raw.strip();
                if (line.isEmpty() || line.startsWith("#")) {
                    continue;
                }
                if (line.startsWith("export ")) {
                    line = line.substring("export ".length()).strip();
                }
                int eq = line.indexOf('=');
                if (eq <= 0) {
                    continue;
                }
                String key = line.substring(0, eq).strip();
                String value = line.substring(eq + 1).strip();
                if (value.length() >= 2
                        && (value.startsWith("\"") && value.endsWith("\"")
                                || value.startsWith("'") && value.endsWith("'"))) {
                    value = value.substring(1, value.length() - 1);
                } else {
                    int comment = value.indexOf(" #");
                    if (comment >= 0) {
                        value = value.substring(0, comment).strip();
                    }
                }
                values.put(key, value);
            }
        } catch (IOException e) {
            throw new UncheckedIOException("Could not read " + file, e);
        }
        return values;
    }
}
