package io.mealie.backend.db;

import static org.assertj.core.api.Assertions.assertThat;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** Storage formats as written by the Python backend; the literal values were copied from a real dev database. */
class SqlDialectTest {

    private final SqlDialect sqlite = SqlDialect.forEngine(DbEngine.SQLITE);
    private final SqlDialect postgres = SqlDialect.forEngine(DbEngine.POSTGRES);

    private static final UUID ID = UUID.fromString("b9dcf0b0-5b3d-4d1c-82ec-384d5cd191dd");

    @Test
    void sqliteUuidIs32CharLowercaseHex() {
        assertThat(sqlite.uuid(ID)).isEqualTo("b9dcf0b05b3d4d1c82ec384d5cd191dd");
        assertThat(sqlite.uuid(UUID.fromString("00000000-0000-0000-0000-00000000000a")))
                .isEqualTo("0000000000000000000000000000000a");
        assertThat(SqlDialect.Sqlite.parseUuid("b9dcf0b05b3d4d1c82ec384d5cd191dd")).isEqualTo(ID);
        assertThat(SqlDialect.Sqlite.parseUuid(ID.toString())).isEqualTo(ID);
    }

    @Test
    void postgresUuidIsNative() {
        assertThat(postgres.uuid(ID)).isEqualTo(ID);
    }

    @Test
    void sqliteBooleansAreIntegers() {
        assertThat(sqlite.bool(true)).isEqualTo(1);
        assertThat(sqlite.bool(false)).isEqualTo(0);
        assertThat(sqlite.bool(null)).isNull();
        assertThat(postgres.bool(true)).isEqualTo(true);
    }

    @Test
    void sqliteTimestampMatchesSqlalchemyFormatInUtc() {
        OffsetDateTime local = OffsetDateTime.of(2026, 10, 9, 6, 56, 9, 915_853_000, ZoneOffset.ofHours(2));
        assertThat(sqlite.timestamp(local)).isEqualTo("2026-10-09 04:56:09.915853");
        assertThat(sqlite.timestamp(local.withNano(0))).isEqualTo("2026-10-09 04:56:09.000000");
        assertThat(postgres.timestamp(local)).isEqualTo(LocalDateTime.of(2026, 10, 9, 4, 56, 9, 915_853_000));
    }

    @Test
    void sqliteDateIsIsoText() {
        assertThat(sqlite.date(LocalDate.of(2026, 1, 2))).isEqualTo("2026-01-02");
    }

    @Test
    void sqliteReadsStoredValues() throws Exception {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite::memory:");
                PreparedStatement st = conn.prepareStatement("""
                        SELECT 'b9dcf0b05b3d4d1c82ec384d5cd191dd' AS id, 1 AS yes, 0 AS no, NULL AS unknown,
                               '2026-10-09 04:56:09.915853' AS ts, '2026-10-09 04:56:09' AS ts_whole,
                               '2026-10-09' AS d, NULL AS missing
                        """);
                ResultSet rs = st.executeQuery()) {
            rs.next();
            assertThat(sqlite.getUuid(rs, "id")).isEqualTo(ID);
            assertThat(sqlite.getBool(rs, "yes")).isTrue();
            assertThat(sqlite.getBool(rs, "no")).isFalse();
            assertThat(sqlite.getBool(rs, "unknown")).isNull();
            assertThat(sqlite.getTimestamp(rs, "ts"))
                    .isEqualTo(OffsetDateTime.of(2026, 10, 9, 4, 56, 9, 915_853_000, ZoneOffset.UTC));
            assertThat(sqlite.getTimestamp(rs, "ts_whole"))
                    .isEqualTo(OffsetDateTime.of(2026, 10, 9, 4, 56, 9, 0, ZoneOffset.UTC));
            assertThat(sqlite.getDate(rs, "d")).isEqualTo(LocalDate.of(2026, 10, 9));
            assertThat(sqlite.getUuid(rs, "missing")).isNull();
            assertThat(sqlite.getTimestamp(rs, "missing")).isNull();
        }
    }
}
