package io.mealie.backend.persistence.typehandler;

import java.sql.CallableStatement;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.time.temporal.ChronoField;
import org.apache.ibatis.type.BaseTypeHandler;
import org.apache.ibatis.type.JdbcType;

/** Maps Mealie's timezone-naive UTC timestamps on both PostgreSQL and SQLite. */
public class OffsetDateTimeTypeHandler extends BaseTypeHandler<OffsetDateTime> {

    private static final DateTimeFormatter SQLITE_READ_FORMAT = new DateTimeFormatterBuilder()
            .appendPattern("yyyy-MM-dd")
            .optionalStart().appendLiteral(' ').optionalEnd()
            .optionalStart().appendLiteral('T').optionalEnd()
            .appendPattern("HH:mm:ss")
            .optionalStart().appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, true).optionalEnd()
            .toFormatter();

    @Override
    public void setNonNullParameter(PreparedStatement ps, int index, OffsetDateTime value, JdbcType jdbcType)
            throws SQLException {
        ps.setObject(index, value.withOffsetSameInstant(ZoneOffset.UTC).toLocalDateTime());
    }

    @Override
    public OffsetDateTime getNullableResult(ResultSet rs, String columnName) throws SQLException {
        return parse(rs.getObject(columnName));
    }

    @Override
    public OffsetDateTime getNullableResult(ResultSet rs, int columnIndex) throws SQLException {
        return parse(rs.getObject(columnIndex));
    }

    @Override
    public OffsetDateTime getNullableResult(CallableStatement cs, int columnIndex) throws SQLException {
        return parse(cs.getObject(columnIndex));
    }

    private static OffsetDateTime parse(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof OffsetDateTime timestamp) {
            return timestamp.withOffsetSameInstant(ZoneOffset.UTC);
        }
        if (value instanceof LocalDateTime timestamp) {
            return timestamp.atOffset(ZoneOffset.UTC);
        }
        return LocalDateTime.parse(value.toString(), SQLITE_READ_FORMAT).atOffset(ZoneOffset.UTC);
    }
}
