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
     * The only constructor of Language enum that takes two arguments: a
     * {@code Locale} and a {@code String}.
     * @param locale a Locale attributed to the Language.
     * @param name a String with the name of the Language in that language.
     */
    Language(Locale locale, String name) {
        this.locale = locale;
        this.name = name;
    }

    /**
     * Returns the {@code Locale} of the enum.
     * @return the Locale of the Language.
     */
    public Locale getLocale() {
        return locale;
    }

    /**
     * Returns the {@code String} with the language name of the enum.
     * @return a String with language name of the enum.
     */
    public String getName() {
        return name;
    }

    /**
     * Returns a {@code Language} based on given {@code String}.
     * @param code a String with the language code. It must not be null
     *             or blank.
     * @return the Language when given String matches enum's Locale language.
     * @throws IllegalArgumentException when given String is null, blank or
     * does not match any language code of Language enums.
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
