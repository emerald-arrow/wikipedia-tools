package io.wikipedia_tools.enums;

import java.util.Locale;

/**
 * Enum for languages supported by the app.
 */
public enum Language {
    ENGLISH(Locale.of("en")),
    POLISH(Locale.of("pl"));

    private final Locale locale;

    /**
     * The constructor for Language enum.
     * @param locale a {@link Locale}.
     */
    Language(Locale locale) {
        this.locale = locale;
    }

    /**
     * Returns enum's {@link Locale}.
     * @return the Locale of the Language enum.
     */
    public Locale getLocale() {
        return locale;
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
