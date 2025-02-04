package io.wikipedia_tools.dao;

import io.wikipedia_tools.models.Classification;

import java.sql.SQLException;
import java.util.List;

/**
 * Interface for obtaining classifications' data from the database.
 */
public interface ClassificationDAO {

    /**
     * Retrieves data from the database about all classifications of a
     * championship and returns it as a {@code List} of {@code Classification}
     * objects.
     * @param championshipId an int with the id of a Championship of which
     *                       all classifications should be retrieved.
     * @return a List of Classification objects that consists of championship's
     * classifications.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    List<Classification> getAll(int championshipId)
        throws SQLException;

    /**
     * Retrieves data from the database about active classifications of a
     * championship and returns it as a {@code List} of {@code Classification}
     * objects.
     * @param championshipId an int with the id of a Championship of which
     *                       active classifications should be retrieved.
     * @return a List of Classification objects that consists of championship's
     * classifications that are marked as active.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    List<Classification> getActive(int championshipId)
        throws SQLException;

    /**
     * Retrieves data from the database about championship's classifications
     * with results attributed to them and returns it as a {@code List} of
     * {@code Classification} objects.
     * @param championshipId an int with the id of a Championship of which
     *                       classifications with sessions results attributed
     *                       to them should be retrieved.
     * @return a List of Classification objects that consists of championship's
     * classifications that have results attributed to them.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    List<Classification> getWithResults(int championshipId)
        throws SQLException;

    /**
     * Retrieves the number of scoring cars in a manufacturer's classification
     * from the database and returns it as an {@code int}.
     * @param classificationId an int with the id of a manufacturer's
     *                         classification.
     * @return an int with the number of cars eligible to score in
     * the classification under given classificationId.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    int getScoringCarsOemClassification(int classificationId)
            throws SQLException;

    /**
     * Retrieves the number of races held in a classification from the database
     * and returns it as an {@code int}.
     * @param classificationId an int with the id of the classification to
     *                         retrieve number of races.
     * @return an int with the number of races held.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    int getNumberOfRacesHeld(int classificationId) throws SQLException;
}
