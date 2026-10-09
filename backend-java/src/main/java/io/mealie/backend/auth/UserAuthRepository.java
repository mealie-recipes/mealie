package io.mealie.backend.auth;

import io.mealie.backend.db.SqlDialect;
import io.mealie.backend.persistence.mapper.UserAuthMapper;
import io.mealie.backend.persistence.model.UserAuthRow;
import java.time.OffsetDateTime;
import java.util.Optional;
import java.util.UUID;
import org.springframework.stereotype.Repository;

@Repository
public class UserAuthRepository {

    public record UserAuthRecord(AuthUser user, OffsetDateTime tokensValidAfter) {
    }

    private final UserAuthMapper mapper;
    private final SqlDialect dialect;

    public UserAuthRepository(UserAuthMapper mapper, SqlDialect dialect) {
        this.mapper = mapper;
        this.dialect = dialect;
    }

    public Optional<UserAuthRecord> findById(UUID userId) {
        return Optional.ofNullable(mapper.findById(dialect.uuid(userId))).map(this::toRecord);
    }

    /** The owner of a long-lived API token, matched on both the exact token string and its user id. */
    public Optional<UserAuthRecord> findByApiToken(String token, UUID userId) {
        return Optional.ofNullable(mapper.findByApiToken(token, dialect.uuid(userId))).map(this::toRecord);
    }

    private UserAuthRecord toRecord(UserAuthRow row) {
        AuthUser user = new AuthUser(
                row.id(), row.username(), row.groupId(), row.householdId(), Boolean.TRUE.equals(row.admin()));
        return new UserAuthRecord(user, row.tokensValidAfter());
    }
}
