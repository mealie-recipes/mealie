package io.mealie.backend.health;

import io.mealie.backend.persistence.mapper.SchemaInfoMapper;
import java.util.Optional;
import org.springframework.stereotype.Repository;

@Repository
public class SchemaInfoRepository {

    private final SchemaInfoMapper mapper;

    public SchemaInfoRepository(SchemaInfoMapper mapper) {
        this.mapper = mapper;
    }

    /** The Alembic revision Python last migrated the shared schema to. */
    public Optional<String> alembicRevision() {
        return Optional.ofNullable(mapper.findAlembicRevision());
    }
}
