package io.wikipedia_tools.utils.db;

import io.wikipedia_tools.utils.db.impl.SQLiteConnection;

import java.sql.Connection;
import java.sql.SQLException;

/**
 * Class that provides connection to the currently used database.
 */
public class DbUtil {

    private DbUtil() {}

    /**
     * Provides connection to the SQLite database, currently used database.
     * @return a {@link Connection} to the SQLite database that is currently
     * used.
     */
    public static Connection getConnection() throws SQLException {
        DbConnection conn = new SQLiteConnection();

        try {
            return conn.getDbConnection();
        } catch (SQLException e) {
            throw new SQLException(e);
        }
    }
}
