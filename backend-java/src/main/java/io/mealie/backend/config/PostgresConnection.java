package io.mealie.backend.config;

import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

/**
 * JDBC connection details derived from the same variables as PostgresProvider in
 * mealie/core/settings/db_providers.py.
 */
public record PostgresConnection(String jdbcUrl, String username, String password) {

    /**
     * Every connection sends String parameters untyped, so the server infers the column type. That lets the same
     * SQL bind plain strings to native enum columns (e.g. users.auth_method) and JSON columns on both engines.
     */
    static final String JDBC_PARAMS = "stringtype=unspecified&ApplicationName=mealie-java";

    public static PostgresConnection fromEnv(MealieEnv env) {
        String override = env.get("POSTGRES_URL_OVERRIDE").filter(s -> !s.isEmpty()).orElse(null);
        if (override != null) {
            return fromUrl(override);
        }
        String host = env.get("POSTGRES_SERVER", "postgres");
        String port = env.get("POSTGRES_PORT", "5432");
        String db = env.get("POSTGRES_DB", "mealie");
        return new PostgresConnection(
                "jdbc:postgresql://" + host + ":" + port + "/" + db + "?" + JDBC_PARAMS,
                env.get("POSTGRES_USER", "mealie"),
                env.get("POSTGRES_PASSWORD", "mealie"));
    }

    /**
     * Parses {@code postgresql://user:password@host:port/db?params}. Like Python's _parse_override_url, the
     * credentials are split on the last '@' and the first ':' and the password is taken literally, so it may contain
     * characters that would break a URI parser.
     */
    static PostgresConnection fromUrl(String url) {
        String prefix = "postgresql://";
        if (!url.startsWith(prefix)) {
            throw new IllegalArgumentException("POSTGRES_URL_OVERRIDE scheme must be postgresql");
        }
        String remainder = url.substring(prefix.length());
        String user = null;
        String password = null;
        int at = remainder.lastIndexOf('@');
        if (at >= 0) {
            String credentials = remainder.substring(0, at);
            remainder = remainder.substring(at + 1);
            int colon = credentials.indexOf(':');
            if (colon >= 0) {
                user = credentials.substring(0, colon);
                password = credentials.substring(colon + 1);
            } else {
                user = credentials;
            }
            user = URLDecoder.decode(user, StandardCharsets.UTF_8);
        }
        String separator = remainder.contains("?") ? "&" : "?";
        return new PostgresConnection("jdbc:postgresql://" + remainder + separator + JDBC_PARAMS, user, password);
    }

    @Override
    public String toString() {
        return "PostgresConnection[jdbcUrl=" + jdbcUrl + ", username=" + username + ", password=******]";
    }
}
