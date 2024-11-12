package io.wikipedia_tools.utils.db.impl;

import io.wikipedia_tools.utils.db.DbConnection;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * Connection to the SQLite database
 */
public class SQLiteConnection implements DbConnection {
    private static final String DB_PATH = ".\\database.db";

    /**
     * Returns connection to the SQLite database.
     * @return a {@code Connection} to the SQLite database under
     * {@code DB_PATH} file path.
     */
    @Override
    public Connection getDbConnection() {
        try {
            return DriverManager.getConnection(String.format("jdbc:sqlite:%s", DB_PATH));
        } catch (SQLException e) {
            System.out.println(e.getLocalizedMessage());
            return null;
        }
    }
}
