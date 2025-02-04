package io.wikipedia_tools.dao;

import io.wikipedia_tools.models.RoundResult;

import java.sql.SQLException;
import java.util.List;

/**
 * Interface for obtaining scores' data from the database.
 */
public interface ScoreDAO {

    /**
     * Retrieves data about {@code Entity}'s results in a classification from
     * the database and returns it as a {@code List} of {@code RoundResult}
     * objects.
     * @param entityId an int with Entity's id whose results should be
     *                 obtained.
     * @param classificationId an int with classification's id from which
     *                         results should be obtained.
     * @return a List of RoundResult objects with Entity's results from the
     * classification under given classificationId.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    List<RoundResult> getEntityResults(
            int entityId, int classificationId
    ) throws SQLException;
}
