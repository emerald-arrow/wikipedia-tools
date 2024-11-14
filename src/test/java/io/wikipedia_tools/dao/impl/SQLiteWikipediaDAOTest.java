package io.wikipedia_tools.dao.impl;

import io.wikipedia_tools.enums.WikipediaVersion;
import io.wikipedia_tools.models.Wikipedia;
import jdk.jfr.Description;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.sql.SQLException;

import static org.junit.jupiter.api.Assertions.*;

class SQLiteWikipediaDAOTest {
    private SQLiteWikipediaDAO dao;

    @BeforeEach
    void init() {
        dao = new SQLiteWikipediaDAO();
    }

    @Test
    @Description("Successfully retrieving data from 'wikipedia' table")
    @DisplayName("Retrieving single Wikipedia version - success")
    void getSuccess() {
        WikipediaVersion wiki = WikipediaVersion.PLWIKI;

        Wikipedia expected = new Wikipedia(1, "plwiki");

        try {
            Wikipedia actual = dao.get(wiki);

            assertEquals(expected, actual);
        } catch (SQLException e) {
            System.out.println(e.getCause().getMessage());
            fail();
        }
    }
}