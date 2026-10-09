package io.mealie.backend.auth;

import java.util.UUID;

/** The authenticated user, as resolved from a Mealie JWT. Declare it as a controller parameter to require auth. */
public record AuthUser(UUID id, String username, UUID groupId, UUID householdId, boolean admin) {
}
