package io.mealie.backend.app;

import io.mealie.backend.app.AppInfoRepository.PublicGroup;
import io.mealie.backend.config.MealieEnv;
import io.mealie.backend.config.MealieSettings;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.springframework.stereotype.Service;

/** Builds the public app information response from the same environment and database as Python. */
@Service
public class AppInfoService {

    private static final List<String> DEFAULT_ALLOWED_IFRAME_HOSTS = List.of(
            "youtube.com", "youtube-nocookie.com", "vimeo.com", "player.vimeo.com");
    private static final Pattern PYTHON_VERSION = Pattern.compile("__version__\\s*=\\s*[\"']([^\"']+)[\"']");

    private final MealieEnv env;
    private final MealieSettings settings;
    private final AppInfoRepository repository;
    private final String version;

    public AppInfoService(MealieEnv env, MealieSettings settings, AppInfoRepository repository) {
        this.env = env;
        this.settings = settings;
        this.repository = repository;
        this.version = pythonVersion(settings.baseDir());
    }

    public AppInfo get() {
        String defaultGroup = env.get("DEFAULT_GROUP", "Home");
        String defaultHousehold = env.get("DEFAULT_HOUSEHOLD", "Family");

        Optional<PublicGroup> group = repository.findPublicGroupByName(defaultGroup);
        String groupSlug = group.map(PublicGroup::slug).orElse(null);
        String householdSlug = groupSlug == null || groupSlug.isEmpty()
                ? null
                : group.flatMap(value -> repository.findPublicHouseholdSlug(value.id(), defaultHousehold))
                        .orElse(null);

        return new AppInfo(
                settings.production(),
                version,
                booleanSetting("IS_DEMO", false),
                booleanSetting("ALLOW_SIGNUP", false),
                booleanSetting("ALLOW_PASSWORD_LOGIN", true),
                groupSlug,
                householdSlug,
                oidcReady(),
                booleanSetting("OIDC_AUTO_REDIRECT", false),
                env.get("OIDC_PROVIDER_NAME", "OAuth"),
                tokenTime(),
                allowedIframeHosts());
    }

    private boolean oidcReady() {
        if (!booleanSetting("OIDC_AUTH_ENABLED", false)
                || env.get("OIDC_CLIENT_ID").isEmpty()
                || env.get("OIDC_CLIENT_SECRET").isEmpty()
                || env.get("OIDC_CONFIGURATION_URL").isEmpty()) {
            return false;
        }
        boolean groupClaimRequired =
                env.get("OIDC_USER_GROUP").isPresent() || env.get("OIDC_ADMIN_GROUP").isPresent();
        return !groupClaimRequired || env.get("OIDC_GROUPS_CLAIM", "groups") != null;
    }

    /** Pydantic's bool parser accepts these textual forms in addition to true/false and 1/0. */
    private boolean booleanSetting(String key, boolean fallback) {
        String value = env.get(key, Boolean.toString(fallback)).strip().toLowerCase(Locale.ROOT);
        return switch (value) {
            case "1", "on", "t", "true", "y", "yes" -> true;
            case "0", "off", "f", "false", "n", "no" -> false;
            default -> throw new IllegalArgumentException(key + " is not a valid boolean");
        };
    }

    private int tokenTime() {
        int hours = Integer.parseInt(env.get("TOKEN_TIME", "48").strip());
        if (hours < 1) {
            throw new IllegalArgumentException("TOKEN_TIME must be at least 1 hour");
        }
        return Math.min(hours, 400 * 24);
    }

    private List<String> allowedIframeHosts() {
        LinkedHashSet<String> hosts = new LinkedHashSet<>(DEFAULT_ALLOWED_IFRAME_HOSTS);
        for (String host : env.get("ALLOWED_IFRAME_HOSTS", "").split(",")) {
            String normalized = host.strip().toLowerCase(Locale.ROOT);
            if (!normalized.isEmpty()) {
                hosts.add(normalized);
            }
        }
        return new ArrayList<>(hosts);
    }

    private static String pythonVersion(Path baseDir) {
        Path init = baseDir.resolve("mealie/__init__.py");
        try {
            Matcher matcher = PYTHON_VERSION.matcher(Files.readString(init));
            if (matcher.find()) {
                return matcher.group(1);
            }
        } catch (IOException ignored) {
            // Source checkouts use "develop". Release builds replace this value in the Python file.
        }
        return "develop";
    }
}
