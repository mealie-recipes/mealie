package io.mealie.backend.app;

import static org.hamcrest.Matchers.nullValue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class AppInfoIntegrationTest {

    private static final String GROUP_ID = "81c3fa6a7b734766af45af76b806aab4";
    private static final String HOUSEHOLD_ID = "b9dcf0b05b3d4d1c82ec384d5cd191dd";

    @TempDir
    static Path dataDir;

    @Autowired
    MockMvc mvc;

    @DynamicPropertySource
    static void mealieEnvironment(DynamicPropertyRegistry registry) {
        registry.add("TESTING", () -> "true");
        registry.add("PRODUCTION", () -> "false");
        registry.add("DATA_DIR", () -> dataDir.toString());
        registry.add("DB_ENGINE", () -> "sqlite");
        registry.add("IS_DEMO", () -> "true");
        registry.add("ALLOW_SIGNUP", () -> "true");
        registry.add("ALLOW_PASSWORD_LOGIN", () -> "false");
        registry.add("TOKEN_TIME", () -> "12000");
        registry.add("ALLOWED_IFRAME_HOSTS", () -> " Example.com, youtube.com, trusted.tld ");
        registry.add("OIDC_AUTH_ENABLED", () -> "true");
        registry.add("OIDC_CLIENT_ID", () -> "client");
        registry.add("OIDC_CLIENT_SECRET", () -> "secret");
        registry.add("OIDC_CONFIGURATION_URL", () -> "https://id.example/.well-known/openid-configuration");
        registry.add("OIDC_USER_CLAIM", () -> "email");
        registry.add("OIDC_AUTO_REDIRECT", () -> "true");
        registry.add("OIDC_PROVIDER_NAME", () -> "Test ID");
    }

    @BeforeAll
    static void createDatabase() throws Exception {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dataDir.resolve("mealie.db"));
                Statement st = conn.createStatement()) {
            st.executeUpdate("CREATE TABLE groups (id CHAR(32) PRIMARY KEY, name VARCHAR, slug VARCHAR)");
            st.executeUpdate("""
                    CREATE TABLE group_preferences (
                        id CHAR(32) PRIMARY KEY, group_id CHAR(32), private_group BOOLEAN)
                    """);
            st.executeUpdate("""
                    CREATE TABLE households (
                        id CHAR(32) PRIMARY KEY, name VARCHAR, slug VARCHAR, group_id CHAR(32))
                    """);
            st.executeUpdate("""
                    CREATE TABLE household_preferences (
                        id CHAR(32) PRIMARY KEY, household_id CHAR(32), private_household BOOLEAN)
                    """);
            st.executeUpdate("INSERT INTO groups VALUES ('" + GROUP_ID + "', 'Home', 'home')");
            st.executeUpdate("INSERT INTO group_preferences VALUES ('00000000000000000000000000000001', '"
                    + GROUP_ID + "', 0)");
            st.executeUpdate("INSERT INTO households VALUES ('" + HOUSEHOLD_ID + "', 'Family', 'family', '"
                    + GROUP_ID + "')");
            st.executeUpdate("INSERT INTO household_preferences VALUES ('00000000000000000000000000000002', '"
                    + HOUSEHOLD_ID + "', 0)");
        }
    }

    @Test
    void returnsTheSamePublicShapeAndSettingsAsPython() throws Exception {
        mvc.perform(get("/api/app/about"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.production").value(false))
                .andExpect(jsonPath("$.version").value("develop"))
                .andExpect(jsonPath("$.demoStatus").value(true))
                .andExpect(jsonPath("$.allowSignup").value(true))
                .andExpect(jsonPath("$.allowPasswordLogin").value(false))
                .andExpect(jsonPath("$.defaultGroupSlug").value("home"))
                .andExpect(jsonPath("$.defaultHouseholdSlug").value("family"))
                .andExpect(jsonPath("$.enableOidc").value(true))
                .andExpect(jsonPath("$.oidcRedirect").value(true))
                .andExpect(jsonPath("$.oidcProviderName").value("Test ID"))
                .andExpect(jsonPath("$.tokenTime").value(9600))
                .andExpect(jsonPath("$.allowedIframeHosts[0]").value("youtube.com"))
                .andExpect(jsonPath("$.allowedIframeHosts[4]").value("example.com"))
                .andExpect(jsonPath("$.allowedIframeHosts[5]").value("trusted.tld"));
    }

    @Test
    void hidesPrivateDefaultSlugsLikePython() throws Exception {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dataDir.resolve("mealie.db"));
                Statement st = conn.createStatement()) {
            st.executeUpdate("UPDATE group_preferences SET private_group = 1");
        }
        mvc.perform(get("/api/app/about"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.defaultGroupSlug").value(nullValue()))
                .andExpect(jsonPath("$.defaultHouseholdSlug").value(nullValue()));
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dataDir.resolve("mealie.db"));
                Statement st = conn.createStatement()) {
            st.executeUpdate("UPDATE group_preferences SET private_group = 0");
        }
    }
}
