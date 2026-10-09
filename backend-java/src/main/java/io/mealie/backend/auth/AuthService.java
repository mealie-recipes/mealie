package io.mealie.backend.auth;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.interfaces.Claim;
import com.auth0.jwt.interfaces.DecodedJWT;
import io.mealie.backend.auth.UserAuthRepository.UserAuthRecord;
import io.mealie.backend.web.ApiException;
import java.time.OffsetDateTime;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

/**
 * Resolves a Mealie JWT to a user with the same rules as get_current_user() in
 * mealie/core/dependencies/dependencies.py:
 * <ul>
 *   <li>HS256 signature; exp, nbf and iat are checked with no leeway (PyJWT's defaults). The issuer is not
 *       checked, because Python doesn't check it either.</li>
 *   <li>A {@code long_token} claim marks an API token: it is only valid while the exact token string is stored in
 *       long_live_tokens for the user in its {@code id} claim.</li>
 *   <li>Otherwise {@code sub} is the user id, and the token is rejected if it was issued before the user's
 *       tokens_valid_after (set on password change).</li>
 * </ul>
 */
@Service
public class AuthService {

    public static final String CREDENTIALS_DETAIL = "Could not validate credentials";

    private final JwtSecret secret;
    private final UserAuthRepository users;

    public AuthService(JwtSecret secret, UserAuthRepository users) {
        this.secret = secret;
        this.users = users;
    }

    public AuthUser authenticate(String token) {
        DecodedJWT jwt = verify(token);

        Claim longToken = jwt.getClaim("long_token");
        if (!longToken.isMissing() && !longToken.isNull()) {
            // Python raises a bare HTTPException(401) on this path, so there is no WWW-Authenticate header.
            return parseUuid(jwt.getClaim("id").asString())
                    .flatMap(userId -> users.findByApiToken(token, userId))
                    .map(UserAuthRecord::user)
                    .orElseThrow(() -> new ApiException(HttpStatus.UNAUTHORIZED));
        }

        UserAuthRecord record = parseUuid(jwt.getSubject())
                .flatMap(users::findById)
                .orElseThrow(AuthService::credentialsException);

        if (record.tokensValidAfter() != null && issuedBefore(jwt, record.tokensValidAfter())) {
            throw credentialsException();
        }
        return record.user();
    }

    private DecodedJWT verify(String token) {
        String key = secret.current().orElseThrow(AuthService::credentialsException);
        try {
            return JWT.require(Algorithm.HMAC256(key)).build().verify(token);
        } catch (JWTVerificationException | IllegalArgumentException e) {
            throw credentialsException();
        }
    }

    /** {@code iat < tokens_valid_after.timestamp()}, where a missing iat counts as issued before. */
    private static boolean issuedBefore(DecodedJWT jwt, OffsetDateTime validAfter) {
        Long issuedAt = jwt.getClaim("iat").asLong();
        if (issuedAt == null) {
            return true;
        }
        long validAfterSeconds = validAfter.toEpochSecond();
        return issuedAt < validAfterSeconds || (issuedAt == validAfterSeconds && validAfter.getNano() > 0);
    }

    private static Optional<UUID> parseUuid(String value) {
        if (value == null) {
            return Optional.empty();
        }
        try {
            return Optional.of(UUID.fromString(value));
        } catch (IllegalArgumentException e) {
            return Optional.empty();
        }
    }

    static ApiException credentialsException() {
        return new ApiException(HttpStatus.UNAUTHORIZED, CREDENTIALS_DETAIL, Map.of("WWW-Authenticate", "Bearer"));
    }
}
