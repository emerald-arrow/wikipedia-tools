package io.wikipedia_tools.dao;

import io.wikipedia_tools.models.LocalizedAbbreviations;

import java.sql.SQLException;

/**
 * Interface for obtaining results styling data from the database.
 */
public interface ResultStylingDAO {

    /**
     * Retrieves data about localized non-classified results abbreviations from
     * the database and returns it as a {@code LocalizedAbbreviations} object.
     * @param wikipediaId an int with Wikipedia's id to look for abbreviations
     *                    dedicated to particular Wikipedia version.
     * @return a LocalisedAbbreviations object with localized abbreviations
     * based on given wikipediaId.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    LocalizedAbbreviations getAbbreviations(int wikipediaId)
            throws SQLException;
}
