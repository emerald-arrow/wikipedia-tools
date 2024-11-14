package io.wikipedia_tools.dao;

import io.wikipedia_tools.enums.WikipediaVersion;
import io.wikipedia_tools.models.Wikipedia;

import java.sql.SQLException;
import java.util.List;

/**
 * Interface for obtaining data from "wikipedia" table in the database.
 */
public interface WikipediaDAO {

    /**
     * Retrieves data about single Wikipedia version from "wikipedia" table.
     * @param wikipediaVersion a {@link WikipediaVersion} used to retrieve
     *                         data from the database.
     * @return a {@link Wikipedia} object with data matching of given enum.
     * @throws SQLException when an error occurs during execution of the
     * query.
     */
    Wikipedia get(WikipediaVersion wikipediaVersion) throws SQLException;

    /**
     * Retrieves data about all Wikipedia versions present in the "wikipedia"
     * table.
     * @return a {@link List} of {@link Wikipedia} objects.
     * @throws SQLException when an error occurs during execution of the
     * query.
     */
    List<Wikipedia> getAll() throws SQLException;
}
