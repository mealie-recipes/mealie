package io.mealie.backend.auth;

import io.mealie.backend.db.SqlDialect;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.Optional;
import java.util.UUID;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class UserAuthRepository {

    public record UserAuthRecord(AuthUser user, OffsetDateTime tokensValidAfter) {
    }

    private static final String USER_COLUMNS =
            "u.id, u.username, u.group_id, u.household_id, u.admin, u.tokens_valid_after";

    private final NamedParameterJdbcTemplate jdbc;
    private final SqlDialect dialect;
    private final RowMapper<UserAuthRecord> mapper;

    public UserAuthRepository(NamedParameterJdbcTemplate jdbc, SqlDialect dialect) {
        this.jdbc = jdbc;
        this.dialect = dialect;
        this.mapper = this::mapRow;
    }

    public Optional<UserAuthRecord> findById(UUID userId) {
        String sql = "SELECT " + USER_COLUMNS + " FROM users u WHERE u.id = :id";
        return jdbc.query(sql, new MapSqlParameterSource("id", dialect.uuid(userId)), mapper).stream().findFirst();
    }

    /** The owner of a long-lived API token, matched on both the exact token string and its user id. */
    public Optional<UserAuthRecord> findByApiToken(String token, UUID userId) {
        String sql = "SELECT " + USER_COLUMNS + " FROM long_live_tokens t JOIN users u ON u.id = t.user_id"
                + " WHERE t.token = :token AND t.user_id = :userId";
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("token", token)
                .addValue("userId", dialect.uuid(userId));
        return jdbc.query(sql, params, mapper).stream().findFirst();
    }

    private UserAuthRecord mapRow(ResultSet rs, int rowNum) throws SQLException {
        AuthUser user = new AuthUser(
                dialect.getUuid(rs, "id"),
                rs.getString("username"),
                dialect.getUuid(rs, "group_id"),
                dialect.getUuid(rs, "household_id"),
                Boolean.TRUE.equals(dialect.getBool(rs, "admin")));
        return new UserAuthRecord(user, dialect.getTimestamp(rs, "tokens_valid_after"));
    }
}
