package io.mealie.backend.auth;

import io.mealie.backend.config.MealieSettings;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.util.Optional;
import org.springframework.stereotype.Component;

/**
 * The HS256 key the Python backend signs tokens with (determine_secrets() in mealie/core/settings/settings.py).
 *
 * <p>In production that is the contents of {@code <DATA_DIR>/.secret}. When PRODUCTION is false (as in
 * {@code task py}) Python ignores the file and uses a fixed key, so Java must do the same. Java only ever reads the
 * file; if it doesn't exist yet, Python creates it on startup, and this class picks it up (and any later
 * replacement) without a restart.
 */
@Component
public class JwtSecret {

    private final MealieSettings settings;

    private record Cached(FileTime modified, String secret) {
    }

    private volatile Cached cached;

    public JwtSecret(MealieSettings settings) {
        this.settings = settings;
    }

    /** Empty when the secret file is missing or blank, in which case no token can be valid. */
    public Optional<String> current() {
        if (!settings.production()) {
            return Optional.of(MealieSettings.NON_PRODUCTION_SECRET);
        }
        Path file = settings.secretFile();
        try {
            FileTime modified = Files.getLastModifiedTime(file);
            Cached snapshot = cached;
            if (snapshot == null || !snapshot.modified().equals(modified)) {
                snapshot = new Cached(modified, Files.readString(file, StandardCharsets.UTF_8).strip());
                cached = snapshot;
            }
            return snapshot.secret().isEmpty() ? Optional.empty() : Optional.of(snapshot.secret());
        } catch (IOException e) {
            return Optional.empty();
        }
    }
}
