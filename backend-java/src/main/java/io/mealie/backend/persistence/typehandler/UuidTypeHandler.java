package io.mealie.backend.persistence.typehandler;

import java.sql.CallableStatement;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HexFormat;
import java.util.UUID;
import org.apache.ibatis.type.BaseTypeHandler;
import org.apache.ibatis.type.JdbcType;

/** Reads Mealie UUIDs from native Postgres UUID columns or SQLAlchemy's 32-character SQLite representation. */
public class UuidTypeHandler extends BaseTypeHandler<UUID> {

    @Override
    public void setNonNullParameter(PreparedStatement ps, int index, UUID value, JdbcType jdbcType)
            throws SQLException {
        if (ps.getConnection().getMetaData().getDatabaseProductName().equalsIgnoreCase("PostgreSQL")) {
            ps.setObject(index, value);
        } else {
            ps.setString(index, toHex(value));
        }
    }

    @Override
    public UUID getNullableResult(ResultSet rs, String columnName) throws SQLException {
        return parse(rs.getObject(columnName));
    }

    @Override
    public UUID getNullableResult(ResultSet rs, int columnIndex) throws SQLException {
        return parse(rs.getObject(columnIndex));
    }

    @Override
    public UUID getNullableResult(CallableStatement cs, int columnIndex) throws SQLException {
        return parse(cs.getObject(columnIndex));
    }

    private static UUID parse(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof UUID uuid) {
            return uuid;
        }
        String hex = value.toString().replace("-", "");
        if (hex.length() != 32) {
            throw new IllegalArgumentException("Not a UUID: " + value);
        }
        return new UUID(HexFormat.fromHexDigitsToLong(hex, 0, 16), HexFormat.fromHexDigitsToLong(hex, 16, 32));
    }

    private static String toHex(UUID value) {
        HexFormat hex = HexFormat.of();
        return hex.toHexDigits(value.getMostSignificantBits()) + hex.toHexDigits(value.getLeastSignificantBits());
    }
}
