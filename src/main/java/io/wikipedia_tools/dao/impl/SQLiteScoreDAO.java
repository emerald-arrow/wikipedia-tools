package io.wikipedia_tools.dao.impl;

import io.wikipedia_tools.dao.ScoreDAO;
import io.wikipedia_tools.enums.Session;
import io.wikipedia_tools.models.ResultStyle;
import io.wikipedia_tools.models.RoundResult;
import io.wikipedia_tools.utils.db.DbUtil;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

/**
 * Class for obtaining scores' data from the SQLite database.
 */
public class SQLiteScoreDAO implements ScoreDAO {

    /**
     * Retrieves data about {@code Entity}'s results in a classification from
     * the SQLite database and returns it as a {@code List} of
     * {@code RoundResult} objects.
     * @param entityId an int with Entity's id whose results should be obtained.
     * @param classificationId an int with classification's id from which
     *                         results should be obtained.
     * @return an unmodifiable List of RoundResult objects with
     * Entity's results from the classification under given classificationId.
     * Results contain only race results as only P1 in qualifying is stored in
     * the database. P1 in qualifying is shown in race's result by making its
     * text weight bold.
     * @throws SQLException when an error occurs while retrieving data from the
     * database.
     */
    @Override
    public List<RoundResult> getEntityResults(
        int entityId, int classificationId
    ) throws SQLException {
        if (!(entityId > 0)) {
            throw new IllegalArgumentException(
                    "Entity's id must be greater than 0."
            );
        }

        if (!(classificationId > 0)) {
            throw new IllegalArgumentException(
                    "Classification's id must be greater than 0."
            );
        }

        String query = """
                SELECT sc.round_number AS ROUND
                , ses.name AS SESSION
                , sc.place AS PLACE
                , sc.points AS POINTS
                , rs.id AS STYLE_ID
                , rs.background_hex AS BACKGROUND
                , rs.text_colour_hex AS TEXT_COLOUR
                , rs.bold AS TEXT_BOLD
                FROM score sc
                JOIN "session" ses
                ON ses.id = sc.session_id
                JOIN result_styling rs
                ON rs.id = sc.style_id
                WHERE classification_id = ?
                AND sc.entity_id = ?
                """;

        List<RoundResult> results = new ArrayList<>();
        RoundResult previousResult = null;

        try (
                var conn = DbUtil.getConnection();
                var ps = conn.prepareStatement(query)
        ) {
            ps.setInt(1, classificationId);
            ps.setInt(2, entityId);

            try (var rs = ps.executeQuery()) {
                while (rs.next()) {
                    final int roundNumber = rs.getInt("ROUND");
                    boolean textBold = false;

                    if (previousResult != null
                            && roundNumber == previousResult.getRoundNumber()
                            && previousResult.isQualifying()
                    ) {
                        textBold = true;
                        results.remove(previousResult);
                    }

                    ResultStyle style = new ResultStyle(
                            rs.getInt("STYLE_ID"),
                            rs.getString("BACKGROUND"),
                            rs.getString("TEXT_COLOUR"),
                            textBold
                    );

                    RoundResult result = new RoundResult(
                            roundNumber,
                            Session.fromString(rs.getString("SESSION")),
                            rs.getString("PLACE"),
                            rs.getDouble("POINTS"),
                            style
                    );

                    results.add(result);
                    previousResult = result;
                }
            }
        }

        return List.copyOf(results);
    }
}
