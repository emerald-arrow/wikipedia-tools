package io.wikipedia_tools.dao.impl;

import io.wikipedia_tools.dao.TeamDAO;
import io.wikipedia_tools.models.Team;
import io.wikipedia_tools.utils.db.DbUtil;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

/**
 * Class for obtaining teams' data from the SQLite database.
 */
public class SQLiteTeamDAO implements TeamDAO {

    /**
     * Retrieves data about teams present in a classification from the SQLite
     * database and returns it as a {@code List} of {@code Team} objects.n.
     * @param classificationId an int with classification's id to look for
     *                         teams' data.
     * @param wikipediaId an int with Wikipedia's id to retrieve data for the
     *                    specific version of Wikipedia.
     * @return an unmodifiable List of Team objects that consists of data about
     * teams present in the classification under given classificationId.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    @Override
    public List<Team> getTeamsInClassification(
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
                , t.codename as CODENAME
                , t.flag AS FLAG
                , tw.short_link AS ARTICLE_LINK
                , t.car_number AS CAR_NUMBER
                FROM score s
                JOIN team t
                ON t.id = s.entity_id
                JOIN team_wikipedia tw
                ON tw.team_id = t.id
                WHERE s.classification_id = ?
                AND tw.wikipedia_id = ?;
                """;

        List<Team> teams = new ArrayList<>();

        try (var conn = DbUtil.getConnection();
             var ps = conn.prepareStatement(query)
        ) {
            ps.setInt(1, classificationId);
            ps.setInt(2, wikipediaId);

            try (var rs = ps.executeQuery()) {
                while (rs.next()) {
                    Team team = new Team(
                            rs.getInt("ID"),
                            rs.getString("CODENAME"),
                            rs.getString("FLAG"),
                            rs.getString("ARTICLE_LINK"),
                            rs.getInt("CAR_NUMBER")
                    );

                    teams.add(team);
                }
            }
        }

        return List.copyOf(teams);
    }
}
