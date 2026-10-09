package io.mealie.backend.auth;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import java.util.Optional;
import org.springframework.http.HttpHeaders;

/** Finds the raw token the same way as get_auth_token() in mealie/core/dependencies/dependencies.py. */
public final class AuthTokens {

    public static final String COOKIE_NAME = "mealie.access_token";

    private AuthTokens() {
    }

    /**
     * The bearer token from the Authorization header (scheme matched case-insensitively), falling back to the
     * session cookie. Empty when the request carries neither.
     */
    public static Optional<String> extract(HttpServletRequest request) {
        String header = request.getHeader(HttpHeaders.AUTHORIZATION);
        if (header != null) {
            int space = header.indexOf(' ');
            String scheme = space >= 0 ? header.substring(0, space) : header;
            if (scheme.equalsIgnoreCase("bearer")) {
                return Optional.of(space >= 0 ? header.substring(space + 1) : "");
            }
        }
        Cookie[] cookies = request.getCookies();
        if (cookies != null) {
            for (Cookie cookie : cookies) {
                if (COOKIE_NAME.equals(cookie.getName())) {
                    return Optional.of(cookie.getValue());
                }
            }
        }
        return Optional.empty();
    }
}
