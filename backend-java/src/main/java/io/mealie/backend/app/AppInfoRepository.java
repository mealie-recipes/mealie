package io.mealie.backend.app;

import io.mealie.backend.db.SqlDialect;
import io.mealie.backend.persistence.mapper.AppInfoMapper;
import java.util.Optional;
import java.util.UUID;
import org.springframework.stereotype.Repository;

/** Reads the public default group and household without applying authenticated tenant scoping. */
@Repository
public class AppInfoRepository {

    private final AppInfoMapper mapper;
    private final SqlDialect dialect;

    public AppInfoRepository(AppInfoMapper mapper, SqlDialect dialect) {
        this.mapper = mapper;
        this.dialect = dialect;
    }

    public Optional<PublicGroup> findPublicGroupByName(String name) {
        return Optional.ofNullable(mapper.findPublicGroupByName(name))
                .map(row -> new PublicGroup(row.id(), row.slug()));
    }

    public Optional<String> findPublicHouseholdSlug(UUID groupId, String name) {
        return Optional.ofNullable(mapper.findPublicHouseholdSlug(dialect.uuid(groupId), name));
    }

    public record PublicGroup(UUID id, String slug) {
    }
}
