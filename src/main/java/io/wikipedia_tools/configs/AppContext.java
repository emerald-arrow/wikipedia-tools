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
     * Changes language used by the app.
     * @param locale a {@link Locale} to switch to that consists of with
     *               language's two-letter code
     *               (<a href="https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes">ISO 639-1</a>).
     * @return a boolean - true when changing language succeeds, false when
     * changing language fails.
     */
    public static boolean changeLanguage(Locale locale) {
        if (locale == null) {
            throw new IllegalArgumentException("Locale must not be null");
        }

        try {
            currentLanguage = Language.fromLanguageCode(locale.getLanguage());

            Localisation.changeBundle(currentLanguage);
            return true;
        } catch (IllegalArgumentException e) {
            return false;
        }
    }

    /**
     * Changes Wikipedia version used by the app.
     * @param version a {@link WikipediaVersion} enum with Wikipedia version
     *                to be changed to.
     * @return a boolean - true when changing version succeeds, false when
     * changing version fails.
     */
    public static boolean changeWikiVersion(WikipediaVersion version) {
        if (currentWikipediaVersion.equals(version)) {
            return true;
        }

        try {
            Wikipedia foundWikipedia = getWikipedia(version);

            if (foundWikipedia != null) {
                currentWikipediaVersion = version;
                currentWikipedia = foundWikipedia;
                return true;
            }

            return false;
        } catch (SQLException e) {
            System.out.println(e.getLocalizedMessage());
            return false;
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
