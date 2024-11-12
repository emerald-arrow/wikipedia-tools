package io.wikipedia_tools.utils.db;

import io.wikipedia_tools.utils.db.impl.SQLiteConnection;

import java.sql.Connection;

/**
 * Connection to the currently used database.
 */
public class DbUtil {

    private DbUtil() {}

    /**
     * Connection to the SQLite database.
     * @return a {@code Connection} to the SQLite database that is currently
     * used.
     */
    public static Connection getConnection() {
        DbConnection conn = new SQLiteConnection();

        return conn.getDbConnection();
    }
}
