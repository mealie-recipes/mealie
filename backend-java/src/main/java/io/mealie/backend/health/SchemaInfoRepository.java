package io.mealie.backend.health;

import java.util.Optional;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class SchemaInfoRepository {

    private final JdbcTemplate jdbc;

    public SchemaInfoRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    /** The Alembic revision Python last migrated the shared schema to. */
    public Optional<String> alembicRevision() {
        return jdbc.queryForList("SELECT version_num FROM alembic_version", String.class).stream().findFirst();
    }
}
