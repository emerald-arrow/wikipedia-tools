package io.wikipedia_tools.configs;

import io.wikipedia_tools.dao.WikipediaDAO;
import io.wikipedia_tools.dao.impl.SQLiteWikipediaDAO;
import io.wikipedia_tools.enums.Language;
import io.wikipedia_tools.enums.WikipediaVersion;
import io.wikipedia_tools.models.Wikipedia;

import java.sql.SQLException;
import java.util.IllegalFormatException;
import java.util.Locale;

/**
 * Class that contains app-wide settings.
 */
public class AppContext {
    private static Language currentLanguage;
    private static WikipediaVersion currentWikipediaVersion;
    private static Wikipedia currentWikipedia;

    /**
     * Sets initial values of settings variables. Default values of
     * currentLanguage, currentWikipediaVersion and currentWikipedia are
     * based on user's system locale. If user's language is not supported by
     * the app the default values are set to English and English Wikipedia.
     */
    public static void init() throws SQLException {
        Locale userLocale = Locale.getDefault();
        String userLanguage = userLocale.getLanguage();

        Language lang = Language.ENGLISH;

        try {
            lang = Language.fromLanguageCode(userLanguage);
            currentLanguage = lang;
        } catch (IllegalArgumentException ignored) {
            currentLanguage = lang;
        }

        currentWikipediaVersion = WikipediaVersion.fromLocale(
                currentLanguage.getLocale()
        );

        try {
            currentWikipedia = getWikipedia(currentWikipediaVersion);
        } catch (SQLException e) {
            throw new SQLException(e);
        }

        if (currentWikipedia == null) {
            throw new IllegalArgumentException(
                    "Wikipedia version was not found in the database."
            );
        }
    }

    /**
     * Returns current {@link Language}.
     * @return the Language from the currentLanguage field.
     */
    public static Language getCurrentLanguage() {
        return currentLanguage;
    }

    /**
     * Prints currently used language and Wikipedia version. In case of any
     * error nothing is printed.
     */
    public static void printCurrentSettings() {
        try {
            String settings = String.format(
                    Localisation.get("main_menu.settings"),
                    currentLanguage.getLocale().getLanguage(),
                    currentWikipediaVersion.name().toLowerCase()
            );

            System.out.println(settings);
        } catch (IllegalFormatException ignored) {

        }
    }

    /**
     * Gets a {@link Wikipedia} object based on given
     * {@link WikipediaVersion} enum.
     * @param wikipediaVersion the WikipediaVersion enum used to retrieve
     *                         data from the database.
     * @return the Wikipedia object retrieved from the database.
     */
    private static Wikipedia getWikipedia(
            WikipediaVersion wikipediaVersion
    ) throws SQLException {
        WikipediaDAO dao = new SQLiteWikipediaDAO();

        Wikipedia wiki;

        try {
            wiki = dao.get(wikipediaVersion);
        } catch (SQLException e) {
            throw new SQLException(e);
        }

        return wiki;
    }
}
