package io.wikipedia_tools.menus.impl;

import io.wikipedia_tools.configs.AppContext;
import io.wikipedia_tools.configs.Localisation;
import io.wikipedia_tools.enums.Language;
import io.wikipedia_tools.menus.Menu;
import io.wikipedia_tools.utils.readers.InputReader;
import io.wikipedia_tools.utils.readers.impl.OptionNumberReader;

import java.io.IOException;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

/**
 * Class that allows changing app's language.
 */
public class SettingsLanguageMenu implements Menu {
    private static final Map<String, Locale> OPTIONS;

    private final InputReader<Integer> reader;

    static {
        OPTIONS = prepareOptions();
    }

    /**
     * The constructor that does not take any arguments. The value of the
     * only non-static field is set without external argument.
     */
    public SettingsLanguageMenu() {
        this.reader = prepareReader();
    }

    /**
     * Starts and runs the menu.
     */
    @Override
    public void start() {
        AppContext.printCurrentSettings();

        Locale chosenLocale = chooseOption();

        if (chosenLocale != null && AppContext.changeLanguage(chosenLocale)) {
            System.out.println(Localisation.get("menu_language.success"));
            new SettingsMenu().start();
        } else {
            System.out.println(Localisation.get("menu_language_fail"));
            new MainMenu().start();
        }
    }

    /**
     * Asks for user input.
     * @return a {@link Locale} chosen by the user.
     */
    private Locale chooseOption() {
        Integer chosenOption;

        try {
            chosenOption = this.reader.read();
        } catch (IOException e) {
            System.out.println(e.getLocalizedMessage());
            return null;
        }

        if (chosenOption != null) {
            String key = OPTIONS.keySet()
                    .toArray(String[]::new)[chosenOption - 1];

            return OPTIONS.get(key);
        }

        return null;
    }

    /**
     * Prepares an unmodifiable {@link Map} of available languages. The order
     * of insertion is preserved due to usage of {@link LinkedHashMap}.
     * @return the unmodifiable Map of available languages that has
     * language's name is the key and language's {@link Locale} is the value.
     */
    private static Map<String, Locale> prepareOptions() {
        Map<String, Locale> options = new LinkedHashMap<>() {
            {
                put(
                        Language.ENGLISH.getName(),
                        Language.ENGLISH.getLocale()
                );
                put(
                        Language.POLISH.getName(),
                        Language.POLISH.getLocale()
                );
            }
        };

        return Collections.unmodifiableMap(options);
    }

    /**
     * Prepares an instance of a class that implements {@link InputReader}
     * interface. The instance features available languages and a massage
     * that is going to be shown to the user.
     * @return an instance of the {@link OptionNumberReader} class with
     * available languages names as options and a localised information for
     * the user as message.
     */
    private InputReader<Integer> prepareReader() {
        return new OptionNumberReader(
                OPTIONS.keySet().toArray(String[]::new),
                Localisation.get("menu_language.msg")
        );
    }
}
