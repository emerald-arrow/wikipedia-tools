package io.wikipedia_tools.utils.db.impl;

import io.wikipedia_tools.utils.db.DbConnection;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * Class for connecting to the SQLite database
 */
public class SQLiteConnection implements DbConnection {
    private static final String DB_PATH = ".\\database.db";

    /**
     * Provides connection to the SQLite database.
     * @return a {@link Connection} to the SQLite database under DB_PATH
     * file path.
     */
    @Override
    public Connection getDbConnection() throws SQLException {
        try {
            return DriverManager.getConnection(
                    String.format("jdbc:sqlite:%s", DB_PATH)
            );
        } catch (SQLException e) {
            throw new SQLException(e);
        }
    }
}
