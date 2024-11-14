package io.wikipedia_tools.dao.impl;

import io.wikipedia_tools.dao.WikipediaDAO;
import io.wikipedia_tools.enums.WikipediaVersion;
import io.wikipedia_tools.models.Wikipedia;
import io.wikipedia_tools.utils.db.DbUtil;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

/**
 * Class that retrieves data from the "wikipedia" table in the SQLite
 * database.
 */
public class SQLiteWikipediaDAO implements WikipediaDAO {

    /**
     * Retrieves data about single Wikipedia version from "wikipedia" table
     * in the SQLite database.
     * @param wikipediaVersion a {@link WikipediaVersion} enum used to
     *                         retrieve data from the database.
     * @return the {@link  Wikipedia} object with data matching given
     * WikipediaVersion enum.
     * @throws SQLException when an error occurs during execution of the
     * query.
     */
    @Override
    public Wikipedia get(WikipediaVersion wikipediaVersion) throws SQLException {
        String query = """
                SELECT id, version
                FROM wikipedia
                WHERE version = ? COLLATE NOCASE;
                """;

        try (var conn = DbUtil.getConnection();
             var ps = conn.prepareStatement(query)
        ) {
            ps.setString(1, wikipediaVersion.name());

            try (var rs = ps.executeQuery()) {
                if (rs.next()) {
                    return new Wikipedia(
                            rs.getInt("id"),
                            rs.getString("version")
                    );
                }
            }
        } catch (SQLException e) {
            throw new SQLException(e);
        }

        return null;
    }

    /**
     * Retrieves data about all Wikipedia versions from "wikipedia" table in
     * the SQLite database.
     * @return an unmodifiable {@link List} of {@link Wikipedia} objects that
     * represent all Wikipedia versions in the database.
     * @throws SQLException when an error occurs during execution of the
     * query.
     */
    @Override
    public List<Wikipedia> getAll() throws SQLException {
        String query = "SELECT id, version FROM wikipedia;";

        List<Wikipedia> versions = new ArrayList<>();

        try (var conn = DbUtil.getConnection();
             var ps = conn.prepareStatement(query);
             var rs = ps.executeQuery()) {

            while (rs.next()) {
                Wikipedia newVersion = new Wikipedia(
                        rs.getInt("id"),
                        rs.getString("version")
                );
                versions.add(newVersion);
            }
        } catch (SQLException e) {
            throw new SQLException(e);
        }

        return List.copyOf(versions);
    }
}
