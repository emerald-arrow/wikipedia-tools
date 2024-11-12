package io.wikipedia_tools.utils.db.impl;

import jdk.jfr.Description;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.sql.SQLException;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.fail;

class SQLiteConnectionTest {
    private SQLiteConnection sqliteConnection;

    @BeforeEach
    public void init() {
        sqliteConnection = new SQLiteConnection();
    }

    @Test
    @Description("Successfully retrieving data from the SQLite database.")
    @DisplayName("Retrieving data from SQLite database - success")
    void retrievingDataSuccess() {
        String query = """
                SELECT id, flag
                FROM driver
                WHERE codename = ?;
                """;

        String codename = "matt campbell";

        int expectedId = 75;
        String expectedFlag = "AUS";

        try (
                var con = sqliteConnection.getDbConnection();
                var ps = con.prepareStatement(query)
        ) {
            ps.setString(1, codename);

            try (var rs = ps.executeQuery()) {
                assertEquals(
                        expectedId,
                        rs.getInt("id"),
                        "id is different"
                );

                assertEquals(
                        expectedFlag,
                        rs.getString("flag"),
                        "flag is different"
                );
            }
        } catch (SQLException e) {
            fail("An SQLException occurred:\n" + e.getMessage());
        }
    }
}