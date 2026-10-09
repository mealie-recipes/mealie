package io.mealie.backend.health;

import io.mealie.backend.auth.AuthService;
import io.mealie.backend.auth.AuthUser;
import io.mealie.backend.db.SqlDialect;
import io.mealie.backend.web.ApiException;
import java.util.Optional;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Service;

@Service
public class HealthService {

    /**
     * @param dbEngine "sqlite" or "postgres", the same values as DB_ENGINE and Python's /api/admin/about dbType
     * @param auth only present when the request carried a token, so the diff test can confirm Java accepts it
     */
    public record Health(String status, String dbEngine, Database database, Auth auth) {
    }

    public record Database(boolean connected, String alembicRevision, String error) {
    }

    public record Auth(boolean authenticated, String userId, String username, String detail) {
    }

    private final SqlDialect dialect;
    private final SchemaInfoRepository schema;
    private final AuthService authService;

    public HealthService(SqlDialect dialect, SchemaInfoRepository schema, AuthService authService) {
        this.dialect = dialect;
        this.schema = schema;
        this.authService = authService;
    }

    public Health check(Optional<String> token) {
        Database database = checkDatabase();
        Auth auth = token.map(this::checkToken).orElse(null);
        return new Health(database.connected() ? "ok" : "unavailable", dialect.engine().settingValue(), database, auth);
    }

    private Database checkDatabase() {
        try {
            return new Database(true, schema.alembicRevision().orElse(null), null);
        } catch (DataAccessException e) {
            return new Database(false, null, e.getMostSpecificCause().getMessage());
        }
    }

    private Auth checkToken(String token) {
        try {
            AuthUser user = authService.authenticate(token);
            return new Auth(true, user.id().toString(), user.username(), null);
        } catch (ApiException e) {
            return new Auth(false, null, null, e.detail());
        } catch (DataAccessException e) {
            return new Auth(false, null, null, "Database unavailable");
        }
    }
}
