package io.wikipedia_tools.dao;

import io.wikipedia_tools.models.Manufacturer;

import java.sql.SQLException;
import java.util.List;

/**
 * Interface for obtaining manufacturers' data from the database.
 */
public interface ManufacturerDAO {

    /**
     * Retrieves data about manufacturers present in a classification from the
     * database and returns it as a {@code List} of {@code Manufacturer}
     * objects.
     * @param classificationId an int with classification's id to look for
     *                         manufacturer's data.
     * @param wikipediaId an int with Wikipedia's id to retrieve data for the
     *                    specific version of Wikipedia.
     * @return a List of Manufacturer objects that consists of data about
     * manufacturers present in the classification under given
     * classificationId.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    List<Manufacturer> getManufacturersInClassification(
        int classificationId, int wikipediaId
    ) throws SQLException;
}
