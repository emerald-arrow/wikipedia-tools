package io.wikipedia_tools.dao.impl;

import io.wikipedia_tools.dao.DriverDAO;
import io.wikipedia_tools.models.Driver;
import io.wikipedia_tools.utils.db.DbUtil;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

/**
 * Class for obtaining drivers' data from the SQLite database.
 */
public class SQLiteDriverDAO implements DriverDAO {

    /**
     * Retrieves data about drivers present in a classification from the SQLite
     * database and returns it as a {@code List} of {@code Driver} objects.
     * @param classificationId an int with classification's id to look for
     *                         drivers' data.
     * @param wikipediaId an int with Wikipedia's id to retrieve data for the
     *                    specific version of Wikipedia.
     * @return an unmodifiable List of Driver objects that consists of data
     * about drivers present in the classification under given
     * classificationId.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    @Override
    public List<Driver> getDriversInClassification(
            int classificationId, int wikipediaId
    ) throws SQLException {
        if (!(classificationId > 0)) {
            throw new IllegalArgumentException(
                    "Championship's id must be greater than 0."
            );
        }

        if (!(wikipediaId > 0)) {
            throw new IllegalArgumentException(
                    "Wikipedia's id must be greater than 0."
            );
        }

        String query = """
                SELECT DISTINCT
                entity_id AS ID
                , d.codename as CODENAME
                , d.flag AS FLAG
                , dw.short_link AS ARTICLE_LINK
                FROM score s
                JOIN driver d
                ON d.id = s.entity_id
                JOIN driver_wikipedia dw
                ON dw.driver_id = d.id
                WHERE s.classification_id = ?
                AND dw.wikipedia_id = ?;
                """;

        List<Driver> drivers = new ArrayList<>();

        try (var conn = DbUtil.getConnection();
             var ps = conn.prepareStatement(query)
        ) {
            ps.setInt(1, classificationId);
            ps.setInt(2, wikipediaId);

            try (var rs = ps.executeQuery()) {
                while (rs.next()) {
                    try {
                        Driver driver = new Driver(
                                rs.getInt("ID"),
                                rs.getString("CODENAME"),
                                rs.getString("FLAG"),
                                rs.getString("ARTICLE_LINK")
                        );

                        drivers.add(driver);
                    } catch (IllegalArgumentException e) {
                        final String newLine = System.lineSeparator();

                        final String data = String.format(
                                "Error while creating Driver with data:%s" +
                                        "id=%s%s" +
                                        "codename=%s%s" +
                                        "flag=%s%s" +
                                        "articleLink=%s",
                                newLine,
                                rs.getString("ID"),
                                newLine,
                                rs.getString("CODENAME"),
                                newLine,
                                rs.getString("FLAG"),
                                newLine,
                                rs.getString("ARTICLE_LINK")
                        );

                        System.err.println(data);

                        System.err.println(e.getMessage());

                        return List.of();
                    }
                }
            }
        }

        return List.copyOf(drivers);
    }
}
