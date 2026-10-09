package io.mealie.backend.auth;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTCreator;
import com.auth0.jwt.algorithms.Algorithm;
import jakarta.servlet.http.Cookie;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Runs the app against a throwaway SQLite database laid out like Python's (CHAR(32) hex ids, 0/1 booleans, text
 * datetimes) and checks every rule in AuthService with tokens shaped like Python's.
 */
@SpringBootTest
@AutoConfigureMockMvc
@Import(AuthIntegrationTest.WhoAmIController.class)
class AuthIntegrationTest {

    static final String SECRET = "secret-from-the-data-dir";
    static final String USER_ID = "b9dcf0b0-5b3d-4d1c-82ec-384d5cd191dd";
    static final String LOCKED_OUT_USER_ID = "f414f6af-f5bc-46de-9116-47464f064456";
    static final String GROUP_ID = "81c3fa6a-7b73-4766-af45-af76b806aab4";

    @TempDir
    static Path dataDir;

    @Autowired
    MockMvc mvc;

    /** Stands in for a migrated endpoint that declares Depends(get_current_user). */
    @RestController
    static class WhoAmIController {
        @GetMapping("/api/test/whoami")
        AuthUser whoami(AuthUser user) {
            return user;
        }
    }

    @DynamicPropertySource
    static void mealieEnvironment(DynamicPropertyRegistry registry) {
        // TESTING resolves DATA_DIR against the base dir; an absolute path stays as is.
        registry.add("TESTING", () -> "true");
        registry.add("PRODUCTION", () -> "true");
        registry.add("DATA_DIR", () -> dataDir.toString());
        registry.add("DB_ENGINE", () -> "sqlite");
    }

    @BeforeAll
    static void createDatabase() throws Exception {
        Files.writeString(dataDir.resolve(".secret"), SECRET + "\n");
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dataDir.resolve("mealie.db"));
                Statement st = conn.createStatement()) {
            st.executeUpdate("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)");
            st.executeUpdate("INSERT INTO alembic_version VALUES ('27621d27c7e1')");
            st.executeUpdate("""
                    CREATE TABLE users (id CHAR(32) NOT NULL PRIMARY KEY, username VARCHAR, admin BOOLEAN,
                        group_id CHAR(32) NOT NULL, household_id CHAR(32), tokens_valid_after DATETIME)""");
            st.executeUpdate("""
                    CREATE TABLE long_live_tokens (id CHAR(32) NOT NULL PRIMARY KEY, name VARCHAR NOT NULL,
                        token VARCHAR NOT NULL, user_id CHAR(32))""");
            st.executeUpdate("INSERT INTO users VALUES ('" + hex(USER_ID) + "', 'admin', 1, '" + hex(GROUP_ID)
                    + "', NULL, NULL)");
            // Password changed at a known time: tokens issued before it are void.
            st.executeUpdate("INSERT INTO users VALUES ('" + hex(LOCKED_OUT_USER_ID) + "', 'kai', 0, '"
                    + hex(GROUP_ID) + "', NULL, '2026-01-01 12:00:00.000000')");
        }
    }

    static String hex(String uuid) {
        return uuid.replace("-", "");
    }

    static String token(String secret, Consumer<JWTCreator.Builder> claims) {
        Instant now = Instant.now().truncatedTo(ChronoUnit.SECONDS);
        JWTCreator.Builder builder = JWT.create()
                .withIssuer("mealie")
                .withIssuedAt(now)
                .withExpiresAt(now.plus(1, ChronoUnit.HOURS));
        claims.accept(builder);
        return builder.sign(Algorithm.HMAC256(secret));
    }

    static String userToken(String userId) {
        return token(SECRET, b -> b.withSubject(userId));
    }

    @Test
    void validTokenResolvesTheUser() throws Exception {
        mvc.perform(get("/api/test/whoami").header("Authorization", "Bearer " + userToken(USER_ID)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(USER_ID))
                .andExpect(jsonPath("$.groupId").value(GROUP_ID))
                .andExpect(jsonPath("$.admin").value(true));
    }

    @Test
    void schemeIsCaseInsensitive() throws Exception {
        mvc.perform(get("/api/test/whoami").header("Authorization", "bearer " + userToken(USER_ID)))
                .andExpect(status().isOk());
    }

    @Test
    void cookieIsTheFallback() throws Exception {
        mvc.perform(get("/api/test/whoami").cookie(new Cookie("mealie.access_token", userToken(USER_ID))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(USER_ID));
    }

    @Test
    void missingTokenIsRejectedLikePython() throws Exception {
        mvc.perform(get("/api/test/whoami"))
                .andExpect(status().isUnauthorized())
                .andExpect(header().string("WWW-Authenticate", "Bearer"))
                .andExpect(jsonPath("$.detail").value("Could not validate credentials"));
    }

    @Test
    void wrongSecretIsRejected() throws Exception {
        String forged = token("shh-secret-test-key", b -> b.withSubject(USER_ID));
        mvc.perform(get("/api/test/whoami").header("Authorization", "Bearer " + forged))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void expiredTokenIsRejected() throws Exception {
        String expired = token(SECRET, b -> b.withSubject(USER_ID)
                .withIssuedAt(Instant.now().minus(2, ChronoUnit.HOURS))
                .withExpiresAt(Instant.now().minus(1, ChronoUnit.SECONDS)));
        mvc.perform(get("/api/test/whoami").header("Authorization", "Bearer " + expired))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void otherAlgorithmsAreRejected() throws Exception {
        String hs512 = JWT.create().withSubject(USER_ID).withIssuedAt(Instant.now())
                .sign(Algorithm.HMAC512(SECRET));
        mvc.perform(get("/api/test/whoami").header("Authorization", "Bearer " + hs512))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void unknownUserIsRejected() throws Exception {
        mvc.perform(get("/api/test/whoami")
                        .header("Authorization", "Bearer " + userToken("00000000-0000-0000-0000-000000000001")))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void tokensIssuedBeforePasswordChangeAreRejected() throws Exception {
        String before = token(SECRET, b -> b.withSubject(LOCKED_OUT_USER_ID)
                .withIssuedAt(Instant.parse("2026-01-01T11:59:59Z")));
        String after = token(SECRET, b -> b.withSubject(LOCKED_OUT_USER_ID)
                .withIssuedAt(Instant.parse("2026-01-01T12:00:00Z")));
        String noIat = JWT.create().withSubject(LOCKED_OUT_USER_ID).sign(Algorithm.HMAC256(SECRET));
        mvc.perform(get("/api/test/whoami").header("Authorization", "Bearer " + before))
                .andExpect(status().isUnauthorized());
        mvc.perform(get("/api/test/whoami").header("Authorization", "Bearer " + noIat))
                .andExpect(status().isUnauthorized());
        mvc.perform(get("/api/test/whoami").header("Authorization", "Bearer " + after))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("kai"));
    }

    @Test
    void apiTokenMustBeStoredForItsUser() throws Exception {
        String stored = token(SECRET, b -> b.withClaim("long_token", true).withClaim("id", USER_ID)
                .withClaim("name", "stored"));
        String notStored = token(SECRET, b -> b.withClaim("long_token", true).withClaim("id", USER_ID)
                .withClaim("name", "revoked"));
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dataDir.resolve("mealie.db"));
                Statement st = conn.createStatement()) {
            st.executeUpdate("INSERT INTO long_live_tokens VALUES ('0000000000000000000000000000000b', 'stored', '"
                    + stored + "', '" + hex(USER_ID) + "')");
        }
        mvc.perform(get("/api/test/whoami").header("Authorization", "Bearer " + stored))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(USER_ID));
        // Python raises a bare HTTPException(401) here: default detail, no WWW-Authenticate.
        mvc.perform(get("/api/test/whoami").header("Authorization", "Bearer " + notStored))
                .andExpect(status().isUnauthorized())
                .andExpect(header().doesNotExist("WWW-Authenticate"))
                .andExpect(jsonPath("$.detail").value("Unauthorized"));
    }

    @Test
    void healthReportsEngineAndTokenState() throws Exception {
        mvc.perform(get("/api/java/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.dbEngine").value("sqlite"))
                .andExpect(jsonPath("$.database.connected").value(true))
                .andExpect(jsonPath("$.database.alembicRevision").value("27621d27c7e1"))
                .andExpect(jsonPath("$.auth").doesNotExist());
        mvc.perform(get("/api/java/health").header("Authorization", "Bearer " + userToken(USER_ID)))
                .andExpect(jsonPath("$.auth.authenticated").value(true))
                .andExpect(jsonPath("$.auth.userId").value(USER_ID));
        mvc.perform(get("/api/java/health").header("Authorization", "Bearer nonsense"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.auth.authenticated").value(false));
    }

    @Test
    void unknownPathsAnswerLikeStarlette() throws Exception {
        mvc.perform(get("/api/foods"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.detail").value("Not Found"));
    }
}
