package io.mealie.backend.db;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.time.temporal.ChronoField;
import java.util.HexFormat;
import java.util.UUID;

/**
 * The single place that knows how SQLite and Postgres differ. Repositories write one SQL string and pass every
 * engine-sensitive value through this class, both when binding parameters and when reading columns.
 *
 * <p>Storage formats are dictated by the Python backend's SQLAlchemy column types:
 * <ul>
 *   <li>GUID (mealie/db/models/_model_utils/guid.py): native {@code uuid} on Postgres, 32-char lowercase hex
 *       (no dashes) in a CHAR(32) on SQLite.</li>
 *   <li>Boolean: native {@code boolean} on Postgres, INTEGER 0/1 on SQLite.</li>
 *   <li>NaiveDateTime (mealie/db/models/_model_utils/datetime.py): UTC with the zone stripped. Postgres
 *       {@code timestamp without time zone}; SQLite TEXT {@code YYYY-MM-DD HH:MM:SS.ffffff}, which must be
 *       written with exactly that shape because SQLite compares it as a string.</li>
 *   <li>Date: native {@code date} on Postgres, TEXT {@code YYYY-MM-DD} on SQLite.</li>
 * </ul>
 *
 * <p>Enums (native types on Postgres, e.g. {@code authmethod}) and JSON columns need no handling here: the Postgres
 * connection uses {@code stringtype=unspecified}, so a String parameter is typed by the server on both engines.
 */
public abstract sealed class SqlDialect {

    public static SqlDialect forEngine(DbEngine engine) {
        return switch (engine) {
            case SQLITE -> new Sqlite();
            case POSTGRES -> new Postgres();
        };
    }

    public abstract DbEngine engine();

    // -- parameters ---------------------------------------------------------------------------------------------

    public abstract Object uuid(UUID value);

    public abstract Object bool(Boolean value);

    /** A UTC instant for a NaiveDateTime column. */
    public abstract Object timestamp(OffsetDateTime value);

    public abstract Object date(LocalDate value);

    // -- columns ------------------------------------------------------------------------------------------------

    public abstract UUID getUuid(ResultSet rs, String column) throws SQLException;

    public Boolean getBool(ResultSet rs, String column) throws SQLException {
        boolean value = rs.getBoolean(column);
        return rs.wasNull() ? null : value;
    }

    /** NaiveDateTime columns hold UTC; the result always carries {@link ZoneOffset#UTC}. */
    public abstract OffsetDateTime getTimestamp(ResultSet rs, String column) throws SQLException;

    public abstract LocalDate getDate(ResultSet rs, String column) throws SQLException;

    static LocalDateTime toUtcLocal(OffsetDateTime value) {
        return value.withOffsetSameInstant(ZoneOffset.UTC).toLocalDateTime();
    }

    static final class Sqlite extends SqlDialect {

        /** SQLAlchemy's SQLite DATETIME storage format: always six fractional digits. */
        private static final DateTimeFormatter WRITE_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSS");

        /** Lenient on read: fraction optional, and 'T' accepted in case a row was written by something else. */
        private static final DateTimeFormatter READ_FORMAT = new DateTimeFormatterBuilder()
                .appendPattern("yyyy-MM-dd")
                .optionalStart().appendLiteral(' ').optionalEnd()
                .optionalStart().appendLiteral('T').optionalEnd()
                .appendPattern("HH:mm:ss")
                .optionalStart().appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, true).optionalEnd()
                .toFormatter();

        @Override
        public DbEngine engine() {
            return DbEngine.SQLITE;
        }

        @Override
        public Object uuid(UUID value) {
            return value == null ? null : toHex(value);
        }

        @Override
        public Object bool(Boolean value) {
            return value == null ? null : (value ? 1 : 0);
        }

        @Override
        public Object timestamp(OffsetDateTime value) {
            return value == null ? null : WRITE_FORMAT.format(toUtcLocal(value));
        }

        @Override
        public Object date(LocalDate value) {
            return value == null ? null : value.toString();
        }

        @Override
        public UUID getUuid(ResultSet rs, String column) throws SQLException {
            String value = rs.getString(column);
            return value == null ? null : parseUuid(value);
        }

        @Override
        public OffsetDateTime getTimestamp(ResultSet rs, String column) throws SQLException {
            String value = rs.getString(column);
            return value == null ? null : LocalDateTime.parse(value, READ_FORMAT).atOffset(ZoneOffset.UTC);
        }

        @Override
        public LocalDate getDate(ResultSet rs, String column) throws SQLException {
            String value = rs.getString(column);
            return value == null ? null : LocalDate.parse(value.length() > 10 ? value.substring(0, 10) : value);
        }

        static String toHex(UUID value) {
            HexFormat hex = HexFormat.of();
            return hex.toHexDigits(value.getMostSignificantBits()) + hex.toHexDigits(value.getLeastSignificantBits());
        }

        /** Accepts the stored 32-char form and, like Python's uuid.UUID(), the dashed form. */
        static UUID parseUuid(String value) {
            String hex = value.replace("-", "");
            if (hex.length() != 32) {
                throw new IllegalArgumentException("Not a UUID: " + value);
            }
            return new UUID(HexFormat.fromHexDigitsToLong(hex, 0, 16), HexFormat.fromHexDigitsToLong(hex, 16, 32));
        }
    }

    static final class Postgres extends SqlDialect {

        @Override
        public DbEngine engine() {
            return DbEngine.POSTGRES;
        }

        @Override
        public Object uuid(UUID value) {
            return value;
        }

        @Override
        public Object bool(Boolean value) {
            return value;
        }

        @Override
        public Object timestamp(OffsetDateTime value) {
            return value == null ? null : toUtcLocal(value);
        }

        @Override
        public Object date(LocalDate value) {
            return value;
        }

        @Override
        public UUID getUuid(ResultSet rs, String column) throws SQLException {
            return rs.getObject(column, UUID.class);
        }

        @Override
        public OffsetDateTime getTimestamp(ResultSet rs, String column) throws SQLException {
            LocalDateTime value = rs.getObject(column, LocalDateTime.class);
            return value == null ? null : value.atOffset(ZoneOffset.UTC);
        }

        @Override
        public LocalDate getDate(ResultSet rs, String column) throws SQLException {
            return rs.getObject(column, LocalDate.class);
        }
    }
}
