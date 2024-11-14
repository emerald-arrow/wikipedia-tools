package io.wikipedia_tools.enums;

import java.util.Locale;

/**
 * Enum for Wikipedia versions supported by the app.
 */
public enum WikipediaVersion {
    ENWIKI(Locale.of("en")),
    PLWIKI(Locale.of("pl"));

    private final Locale locale;

    /**
     * The constructor of WikipediaVersion enum.
     * @param locale a {@link Locale}.
     */
    WikipediaVersion(Locale locale) {
        this.locale = locale;
    }

    /**
     * Returns a WikipediaVersion based on given {@link String}.
     * @param code a String with Wikipedia version's name (eg. enwiki, plwiki)
     * @return the WikipediaVersion that's name equals given code.
     * @throws IllegalArgumentException when given code does not match any
     * enum's name.
     */
    public static WikipediaVersion fromString(String code) {
        if (code == null || code.isBlank()) {
            throw new IllegalArgumentException(
                    "Code must neither be null nor blank."
            );
        }

        for (WikipediaVersion version : WikipediaVersion.values()) {
            if (version.name().equalsIgnoreCase(code)) {
                return version;
            }
        }

        throw new IllegalArgumentException(
                code + " is not available Wikipedia version."
        );
    }

    /**
     * Returns a WikipediaVersion based on given {@link Locale}.
     * @param locale a Locale
     * @return the WikipediaVersion when given Locale matches enum's Locale.
     * @throws IllegalArgumentException when given Locale does not match any
     * enum's Locale;
     */
    public static WikipediaVersion fromLocale(Locale locale) {
        if (locale == null) {
            throw new IllegalArgumentException("Locale must not be null.");
        }

        for (WikipediaVersion version : WikipediaVersion.values()) {
            if (version.locale.getLanguage().equals(locale.getLanguage())) {
                return version;
            }
        }

        throw new IllegalArgumentException(
                "There is not Wikipedia version with given Locale."
        );
    }
}
