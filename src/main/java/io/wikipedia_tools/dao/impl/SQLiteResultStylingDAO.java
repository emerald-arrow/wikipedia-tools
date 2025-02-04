package io.wikipedia_tools.dao.impl;

import io.wikipedia_tools.dao.ResultStylingDAO;
import io.wikipedia_tools.models.Abbreviation;
import io.wikipedia_tools.models.LocalizedAbbreviations;
import io.wikipedia_tools.utils.db.DbUtil;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

/**
 * Class for obtaining results styling data from the SQLite database.
 */
public class SQLiteResultStylingDAO implements ResultStylingDAO {

    /**
     * Retrieves data about localized non-classified results abbreviations from
     * the SQLite database and returns it as a {@code LocalizedAbbreviations}
     * object.
     * @param wikipediaId an int with Wikipedia's id to look for abbreviations
     *                    dedicated to particular Wikipedia version.
     * @return a LocalisedAbbreviations object with localized abbreviations
     * based on given wikipediaId.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    @Override
    public LocalizedAbbreviations getAbbreviations(int wikipediaId)
            throws SQLException {
        if (!(wikipediaId > 0)) {
            throw new IllegalArgumentException(
                    "Wikipedia's id must not be less than 1."
            );
        }

        String query = """
                SELECT style_id AS STYLE_ID
                , code AS ABBREVIATION
                FROM localised_status
                WHERE wikipedia_id = ?;
                """;

        List<Abbreviation> abbreviations = new ArrayList<>();

        try (
                var conn = DbUtil.getConnection();
                var ps = conn.prepareStatement(query)
        ) {
            ps.setInt(1, wikipediaId);

            try (var rs = ps.executeQuery()) {
                while (rs.next()) {
                    Abbreviation abbr = new Abbreviation(
                            rs.getInt("STYLE_ID"),
                            rs.getString("ABBREVIATION")
                    );

                    abbreviations.add(abbr);
                }
            }
        }

        return new LocalizedAbbreviations(abbreviations);
    }
}
