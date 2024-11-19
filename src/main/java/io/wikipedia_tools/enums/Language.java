package io.wikipedia_tools.enums;

import java.util.Locale;

/**
 * Enum for languages supported by the app.
 */
public enum Language {
    ENGLISH(Locale.of("en"), "English"),
    POLISH(Locale.of("pl"), "polski");

    private final Locale locale;
    private final String name;

    /**
     * The constructor of Language enum.
     * @param locale a {@link Locale} attributed to the Language.
     * @param name a {@link String} with the name of the Language in that
     *             language.
     */
    Language(Locale locale, String name) {
        this.locale = locale;
        this.name = name;
    }

    /**
     * Returns enum's {@link Locale}.
     * @return the Locale of the Language enum.
     */
    public Locale getLocale() {
        return locale;
    }

    /**
     * Returns enum's language name.
     * @return a {@link String} with enum's language name in that language.
     */
    public String getName() {
        return name;
    }

    /**
     * Returns a Language based on given {@link String} that contains
     * a language code.
     * @param code the String with the language code. It must not be null
     *             or blank.
     * @return the Language when given String matches enum's Locale language.
     * @throws IllegalArgumentException when given String does not match any
     * enum's Locale language.
     */
    public static Language fromLanguageCode(String code) {
        if (code == null || code.isBlank()) {
            throw new IllegalArgumentException(
                    "Code must neither be null nor blank."
            );
        }

        for (Language lang : Language.values()) {
            if (lang.locale.getLanguage().equalsIgnoreCase(code)) {
                return lang;
            }
        }

        throw new IllegalArgumentException(
                code + " does not match any Language."
        );
    }
}
