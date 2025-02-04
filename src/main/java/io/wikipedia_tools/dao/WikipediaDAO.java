package io.wikipedia_tools.dao;

import io.wikipedia_tools.enums.WikipediaVersion;
import io.wikipedia_tools.models.Wikipedia;

import java.sql.SQLException;
import java.util.List;

/**
 * Interface for obtaining Wikipedia data from the database.
 */
public interface WikipediaDAO {

    /**
     * Retrieves data about single Wikipedia version from the database and
     * returns it as a {@code Wikipedia} object.
     * @param wikipediaVersion a WikipediaVersion used to retrieve data from
     *                         the database.
     * @return a Wikipedia object with data matching given wikipediaVersion.
     * @throws SQLException when an error occurs during execution of the
     * query.
     */
    Wikipedia get(WikipediaVersion wikipediaVersion) throws SQLException;

    /**
     * Retrieves data about all Wikipedia versions from the database and
     * returns it as a {@code List} of {@code Wikipedia} objects.
     * @return a List of Wikipedia objects that consists of all Wikipedia
     * versions stored in the database.
     * @throws SQLException when an error occurs during execution of the
     * query.
     */
    List<Wikipedia> getAll() throws SQLException;
}
