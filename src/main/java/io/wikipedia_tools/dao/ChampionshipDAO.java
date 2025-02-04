package io.wikipedia_tools.dao;

import io.wikipedia_tools.models.Championship;

import java.sql.SQLException;
import java.util.List;

/**
 * Interface for obtaining championships' data from the database.
 */
public interface ChampionshipDAO {

    /**
     * Retrieves data about all championships from the database and returns it
     * as a {@code List} of {@code Championship} objects.
     * @return a List of Championship objects that consists of all
     * championships stored in the database.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    List<Championship> getAll() throws SQLException;

    /**
     * Retrieves data about championships that have classifications attributed
     * to them from the database and returns it as a {@code List} of
     * {@code Championship} objects.
     * @return a List of Championship objects that consists of championships
     * from the database which have classifications attributed to them via
     * foreign keys.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    List<Championship> getAllWithClassifications() throws SQLException;

    /**
     * Retrieves data about championships that have results attributed to them
     * from the database and returns it as a {@code List} of
     * {@code Championship} objects.
     * @return a List of Championship objects that consists of championships
     * from the database which have session results attributed to them via
     * foreign keys and are marked as active.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    List<Championship> getWithActiveResults() throws SQLException;
}
