package io.wikipedia_tools.dao;

import io.wikipedia_tools.models.Driver;

import java.sql.SQLException;
import java.util.List;

/**
 * Interface for obtaining drivers' data from the database.
 */
public interface DriverDAO {

    /**
     * Retrieves data about drivers present in a classification from the
     * database and returns it as a {@code List} of {@code Driver} objects.
     * @param classificationId an int with classification's id to look for
     *                         drivers' data.
     * @param wikipediaId an int with Wikipedia's id to retrieve data for the
     *                    specific version of Wikipedia.
     * @return a List of Driver objects that consists of data about drivers
     * present in the classification under given classificationId.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    List<Driver> getDriversInClassification(
        int classificationId, int wikipediaId
    ) throws SQLException;
}
