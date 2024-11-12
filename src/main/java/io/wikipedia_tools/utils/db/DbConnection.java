package io.wikipedia_tools.utils.db;

import java.sql.Connection;

/**
 * Classes that implement this interface return a connection to the database
 */
public interface DbConnection {

    /**
     * Establishes connection to the database and returns that connection.
     * @return {@link java.sql.Connection} to the database.
     */
    Connection getDbConnection();
}
