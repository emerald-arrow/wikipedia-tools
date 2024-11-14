package io.wikipedia_tools.configs;

import io.wikipedia_tools.enums.Language;

import java.util.Locale;
import java.util.MissingResourceException;
import java.util.ResourceBundle;

/**
 * Class that stores data about localisation. It allows to retrieve localised
 * labels.
 */
public class Localisation {
    private static final String BUNDLE_NAME = "io.wikipedia_tools.labels";

    private static ResourceBundle bundle;

    /**
     * Sets the initial {@link  Locale} of the {@link ResourceBundle}.
     * @param language a {@link Language} used to set the initial Locale of
     *                 the bundle.
     */
    public static void init(Language language) {
        changeBundle(language);
    }

    /**
     * Returns localised label from {@link ResourceBundle} based on given
     * {@link String}.
     * @param key the String with value used to retrieve localised text.
     * @return the String with localised text or empty String if a value
     * cannot be found for given key.
     */
    public static String get(String key) {
        if (key == null) {
            throw new IllegalArgumentException("Key must not be null.");
        }

        if (key.isBlank()) {
            throw new IllegalArgumentException("Key must not be blank.");
        }

        try {
            return bundle.getString(key);
        } catch (MissingResourceException ignored) {
            return "";
        }
    }

    /**
     * Changes locale of the bundle.
     * @param language a {@link Language} used to change locale of the
     *                 bundle.
     */
    public static void changeBundle(Language language) {
        bundle = ResourceBundle.getBundle(BUNDLE_NAME, language.getLocale());
    }
}
