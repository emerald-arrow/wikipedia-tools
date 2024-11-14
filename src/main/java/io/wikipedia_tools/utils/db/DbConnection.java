package io.wikipedia_tools.utils.db;

import java.sql.Connection;
import java.sql.SQLException;

/**
 * Interface for classes that establish connections to databases.
 */
public interface DbConnection {

    /**
     * Provides {@link Connection} to app's database.
     * @return the Connection to app's database.
     */
    Connection getDbConnection() throws SQLException;
}
