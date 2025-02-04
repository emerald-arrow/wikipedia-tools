package io.wikipedia_tools.dao.impl;

import io.wikipedia_tools.dao.ClassificationDAO;
import io.wikipedia_tools.models.Classification;
import io.wikipedia_tools.utils.db.DbUtil;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

/**
 * Class for retrieving classifications' data from the SQLite database.
 */
public class SQLiteClassificationDAO implements ClassificationDAO {

    /**
     * Retrieves data from the SQLite database about all classifications of a
     * championship and returns it as a {@code List} of {@code Classification}
     * objects.
     * @param championshipId an int with the id of a Championship of which
     *                       all classifications should be retrieved.
     * @return an unmodifiable List of Classification objects that consists of
     * championship's classifications.
     * @throws SQLException when an error occurs while retrieving data.
     */
    @Override
    public List<Classification> getAll(int championshipId)
            throws SQLException {
        if (!(championshipId > 0)) {
            throw new IllegalArgumentException(
                    "Championship's id must be greater than 0."
            );
        }

        String query = """
                SELECT
                cl.id AS C_ID
                , t.name AS C_TITLE
                , cl.season AS C_SEASON
                , cl.races_number AS C_RACES
                , ct.name AS CT_TYPE
                FROM classification cl
                JOIN title t
                ON t.id = cl.title_id
                JOIN classification_type ct
                ON t.type_id = ct.id
                WHERE t.championship_id = ?;
                """;

        return List.copyOf(getClassificationsByChampionshipId(
                query, championshipId
        ));
    }

    /**
     * Retrieves data from the SQLite database about active classifications of
     * a championship and returns it as a {@code List} of
     * {@code Classification} objects.
     * @param championshipId an int with the id of a Championship of which
     *                       active classifications should be retrieved.
     * @return an unmodifiable List of Classification objects that consists of
     * championship's classifications that are marked as active.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    @Override
    public List<Classification> getActive(int championshipId)
            throws SQLException {
        if (!(championshipId > 0)) {
            throw new IllegalArgumentException(
                    "Championship's id must be greater than 0."
            );
        }

        String query = """
                SELECT
                cl.id AS C_ID
                , t.name AS C_TITLE
                , cl.season AS C_SEASON
                , cl.races_number AS C_RACES
                , ct.name AS CT_TYPE
                FROM classification cl
                JOIN title t
                ON t.id = cl.title_id
                JOIN classification_type ct
                ON t.type_id = ct.id
                WHERE t.championship_id = ?
                AND cl.active = 1;
                """;

        return List.copyOf(getClassificationsByChampionshipId(
                query, championshipId
        ));
    }

    /**
     * Retrieves data from the SQLite database about championship's
     * classifications with results attributed to them and returns it as a
     * {@code List} of {@code Classification} objects.
     * @param championshipId an int with the id of a Championship of which
     *                       classifications with sessions results attributed
     *                       to them should be retrieved.
     * @return an unmodifiable List of Classification objects that consists of
     * championship's classifications that have results attributed to them.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    @Override
    public List<Classification> getWithResults(int championshipId)
            throws SQLException {
        if (!(championshipId > 0)) {
            throw new IllegalArgumentException(
                    "Championship's id must be greater than 0."
            );
        }

        String query = """
                SELECT DISTINCT
                cl.id AS C_ID
                , t.name AS C_TITLE
                , cl.season AS C_SEASON
                , cl.races_number AS C_RACES
                , ct.name AS CT_TYPE
                FROM classification cl
                JOIN title t
                ON t.id = cl.title_id
                JOIN classification_type ct
                ON t.type_id = ct.id
                JOIN score s
                ON s.classification_id = cl.id
                WHERE t.championship_id = ?
                AND cl.active = 1;
                """;

        return List.copyOf(getClassificationsByChampionshipId(
                query, championshipId
        ));
    }

    /**
     * Retrieves the number of scoring cars in a manufacturer's classification
     * from the SQLite database and returns it as an {@code int}.
     * @param classificationId an int with the id of manufacturer's
     *                         classification to retrieve number of scoring
     *                         cars.
     * @return an int with the number of cars eligible to score in
     * the classification.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    @Override
    public int getScoringCarsOemClassification(int classificationId)
            throws SQLException {
        if (!(classificationId > 0)) {
            throw new IllegalArgumentException(
                    "Classification's id must be greater than 0."
            );
        }

        String query = """
                SELECT scoring_cars AS CARS
                FROM manufacturer_classification
                WHERE manufacturer_classification_id = ?;
                """;

        try (var conn = DbUtil.getConnection();
             var ps = conn.prepareStatement(query)
        ) {
            ps.setInt(1, classificationId);

            try (var rs = ps.executeQuery()) {
                return rs.getInt("CARS");
            }
        }
    }

    /**
     * Retrieves the number of races held in a classification from the SQLite
     * database and returns it as an {@code int}.
     * @param classificationId an int with the id of the classification to
     *                         retrieve number of races.
     * @return an int with the number of races held in the classification under
     * given classificationId.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    @Override
    public int getNumberOfRacesHeld(int classificationId) throws SQLException {
        if (!(classificationId > 0)) {
            throw new IllegalArgumentException(
                    "Classification's id must be greater than 0."
            );
        }

        String query = """
                SELECT MAX(round_number) as RACES_HELD
                FROM score
                WHERE classification_id = ?;
                """;

        try (var conn = DbUtil.getConnection();
             var ps = conn.prepareStatement(query)
        ) {
            ps.setInt(1, classificationId);

            try (var rs = ps.executeQuery()) {
                return rs.getInt("RACES_HELD");
            }
        }
    }

    /**
     * Executes a query and retrieves data about classifications, returns
     * obtained data as a {@code List} of {@code Classification}.
     * @param query a String with SQL query that must have one question mark to
     *              set championship's id in the PreparedStatement.
     * @param championshipId an int with championship's id whose
     *                       classifications should be retrieved. It is used in
     *                       PreparedStatement.
     * @return an ArrayList with classifications that meet query's criteria.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    private List<Classification> getClassificationsByChampionshipId(
            String query, int championshipId
    ) throws SQLException {
        if (query == null || query.isBlank()) {
            throw new IllegalArgumentException(
                    "Query must be neither null nor blank."
            );
        }

        List<Classification> classifications = new ArrayList<>();

        try (var conn = DbUtil.getConnection();
             var ps = conn.prepareStatement(query)
        ) {
            ps.setInt(1, championshipId);

            try (var rs = ps.executeQuery()) {
                while (rs.next()) {
                    try {
                        Classification newClassification = new Classification(
                                rs.getInt("C_ID"),
                                rs.getString("C_TITLE"),
                                rs.getString("C_SEASON"),
                                rs.getInt("C_RACES"),
                                rs.getString("CT_TYPE")
                        );

                        classifications.add(newClassification);
                    } catch (InstantiationException e) {
                        String newLine = System.lineSeparator();

                        String error = String.format(
                                "Couldn't create object with data:" +
                                        "id=%s%s" +
                                        ", title=%s%s" +
                                        ", season=%s%s" +
                                        ", races=%s%s" +
                                        ", type=%s",
                                rs.getString("C_ID"),
                                newLine,
                                rs.getString("C_TITLE"),
                                newLine,
                                rs.getString("C_SEASON"),
                                newLine,
                                rs.getString("C_RACES"),
                                newLine,
                                rs.getString("CT_TYPE")
                        );
                        System.err.println(error);
                    }
                }
            }
        }

        return classifications;
    }
}