package io.wikipedia_tools.dao.impl;

import io.wikipedia_tools.dao.ChampionshipDAO;
import io.wikipedia_tools.models.Championship;
import io.wikipedia_tools.utils.db.DbUtil;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

/**
 * Class for retrieving championships' data from the SQLite database.
 */
public class SQLiteChampionshipDAO implements ChampionshipDAO {

    /**
     * Retrieves data about all championships from the SQLite database and
     * returns it as a {@code List} of {@code Championship} objects.
     * @return an unmodifiable List of Championship objects that consists of
     * all championships stored in the database. Objects are created by the
     * constructor that takes three arguments and assigns data to all fields of
     * that class.
     * @throws SQLException when an error occurs while retrieving data.
     */
    @Override
    public List<Championship> getAll() throws SQLException {
        String query = """
                SELECT
                c.id AS C_ID,
                c.name AS C_NAME,
                o.name AS O_NAME
                FROM championship c
                JOIN organiser o
                ON c.organiser_id = o.id;
                """;

        List<Championship> championships = new ArrayList<>();

        try (var conn = DbUtil.getConnection();
             var ps = conn.prepareStatement(query);
             var rs = ps.executeQuery()) {

            while (rs.next()) {
                Championship newChampionship = new Championship(
                        rs.getInt("C_ID"),
                        rs.getString("C_NAME"),
                        rs.getString("O_NAME")
                );
                championships.add(newChampionship);
            }
        }

        return List.copyOf(championships);
    }

    /**
     * Retrieves data about championships that have classifications attributed
     * to them from the SQLite database and returns it as a {@code List} of
     * {@code Championship} objects.
     * @return an unmodifiable List of Championship objects that consists of
     * championships from the database which have classifications attributed to
     * them via foreign keys. Objects are created by the constructor that takes
     * two arguments and assigns data to two out of three fields of the class.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    @Override
    public List<Championship> getAllWithClassifications() throws SQLException {
        String query = """
                SELECT DISTINCT ch.id, ch.name
                FROM championship ch
                JOIN title t
                ON t.championship_id = ch.id;
                """;

        List<Championship> championships = getChampionshipsByIdAndName(query);

        return List.copyOf(championships);
    }

    /**
     * Retrieves data about championships that have active results attributed
     * to them from the SQLite database and returns it as a {@code List} of
     * {@code Championship} objects.
     * @return an unmodifiable List of Championship objects that consists of
     * championships from the database which have session
     * results attributed to them via foreign keys and are marked as active.
     * Objects are created by the constructor that takes two arguments and
     * assigns data about to two out of three fields of the class.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    @Override
    public List<Championship> getWithActiveResults() throws SQLException {
        String query = """
                SELECT DISTINCT ch.id, ch.name
                FROM championship ch
                JOIN title t
                ON t.championship_id = ch.id
                JOIN classification cl
                ON cl.title_id = t.id
                JOIN score s
                ON s.classification_id = cl.id
                WHERE cl.active = 1;
                """;

        List<Championship> championships = getChampionshipsByIdAndName(query);

        return List.copyOf(championships);
    }

    /**
     * Retrieves data from the SQLite database about championships using
     * provided SQL query.
     * @param query a String with the SQL query to execute. It must
     *              have two columns in SELECT: "id" and "name".
     * @return an ArrayList of Championship objects that meet query's criteria.
     * @throws SQLException when an error occurs while retrieving data from
     * the database.
     */
    private List<Championship> getChampionshipsByIdAndName(String query)
            throws SQLException {
        List<Championship> championships = new ArrayList<>();
        if (query == null || query.isBlank()) {
            throw new IllegalArgumentException(
                    "Query must be neither null nor blank."
            );
        }

        try (var conn = DbUtil.getConnection();
             var ps = conn.prepareStatement(query);
             var rs = ps.executeQuery()) {
            while (rs.next()) {
                Championship newChampionship = new Championship(
                        rs.getInt("id"),
                        rs.getString("name")
                );
                championships.add(newChampionship);
            }
        }

        return championships;
    }
}
