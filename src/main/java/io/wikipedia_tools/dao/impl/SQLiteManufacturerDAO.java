package io.wikipedia_tools.dao.impl;

import io.wikipedia_tools.dao.ManufacturerDAO;
import io.wikipedia_tools.models.Manufacturer;
import io.wikipedia_tools.utils.db.DbUtil;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

/**
 * Class for obtaining manufacturers' data from the SQLite database.
 */
public class SQLiteManufacturerDAO implements ManufacturerDAO {

    /**
     * Retrieves data about manufacturers present in a classification from the
     * SQLite database and returns it as a {@code List} of {@code Manufacturer}
     * objects.
     * @param classificationId an int with classification's id to look for
     *                         manufacturer's data.
     * @param wikipediaId an int with Wikipedia's id to retrieve data for the
     *                    specific version of Wikipedia.
     * @return an unmodifiable List of Manufacturer objects that consists of
     * data about manufacturers present in the classification under given
     * classificationId.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    @Override
    public List<Manufacturer> getManufacturersInClassification(
            int classificationId, int wikipediaId
    ) throws SQLException {
        if (!(classificationId > 0)) {
            throw new IllegalArgumentException(
                    "Classification's id must be greater than 0."
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
                , m.codename as CODENAME
                , m.flag AS FLAG
                , mw.link AS ARTICLE_LINK
                FROM score s
                JOIN manufacturer m
                ON m.id = s.entity_id
                JOIN manufacturer_wikipedia mw
                ON mw.manufacturer_id = m.id
                WHERE s.classification_id = ?
                AND mw.wikipedia_id = ?;
                """;

        List<Manufacturer> manufacturers = new ArrayList<>();

        try (var conn = DbUtil.getConnection();
             var ps = conn.prepareStatement(query)
        ) {
            ps.setInt(1, classificationId);
            ps.setInt(2, wikipediaId);

            try (var rs = ps.executeQuery()) {
                while (rs.next()) {
                    try {
                        Manufacturer oem = new Manufacturer(
                                rs.getInt("ID"),
                                rs.getString("CODENAME"),
                                rs.getString("FLAG"),
                                rs.getString("ARTICLE_LINK")
                        );

                        manufacturers.add(oem);
                    } catch (IllegalArgumentException e) {
                        final String newLine = System.lineSeparator();

                        final String data = String.format(
                                "Error while creating Manufacturer with" +
                                        "data:%s" +
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

        return List.copyOf(manufacturers);
    }
}
