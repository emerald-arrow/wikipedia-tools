package io.wikipedia_tools.dao;

import io.wikipedia_tools.models.Team;

import java.sql.SQLException;
import java.util.List;

/**
 * Interface for obtaining teams' data from the database.
 */
public interface TeamDAO {

    /**
     * Retrieves data about teams present in a classification from the database
     * and returns it as a {@code List} of {@code Team} objects.
     * @param classificationId an int with classification's id to look for
     *                         teams' data.
     * @param wikipediaId an int with Wikipedia's id to retrieve data for the
     *                    specific version of Wikipedia.
     * @return a List of Team objects that consists of data about teams present
     * in the classification under given classificationId.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    List<Team> getTeamsInClassification(
            int classificationId, int wikipediaId
    ) throws SQLException;
}
