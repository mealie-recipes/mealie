package io.mealie.backend.persistence.model;

import java.time.OffsetDateTime;
import java.util.UUID;

/** Database projection used by the authentication mapper. */
public record UserAuthRow(
        UUID id,
        String username,
        UUID groupId,
        UUID householdId,
        Boolean admin,
        OffsetDateTime tokensValidAfter) {
}
