package io.wikipedia_tools.menus.impl;

import io.wikipedia_tools.configs.AppContext;
import io.wikipedia_tools.configs.Localisation;
import io.wikipedia_tools.menus.Menu;
import io.wikipedia_tools.utils.readers.InputReader;
import io.wikipedia_tools.utils.readers.impl.OptionNumberReader;

import java.io.IOException;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Class for the first menu shown to the user.
 */
public class MainMenu implements Menu {
    private final Map<String, Menu> menuOptions;
    private final InputReader<Integer> reader;

    /**
     * The constructor that does not take any arguments. Values of all fields
     * are set without them.
     */
    public MainMenu() {
        this.menuOptions = prepareMenuOptions();

        this.reader = prepareReader();
    }

    /**
     * Starts and runs the menu.
     */
    @Override
    public void start() {
        AppContext.printCurrentSettings();

        int option;

        try {
            option = this.reader.read();
        } catch (IOException e) {
            System.out.println(e.getLocalizedMessage());
            return;
        }

        String key = this.menuOptions.keySet()
                .toArray(String[]::new)[option - 1];

        this.menuOptions.get(key).start();
    }

    /**
     * Prepares a {@link LinkedHashMap} of localised {@link Menu} options to
     * be set as MainMenu's menuOptions field.
     * @return the unmodifiable {@link Map} of Menu options. All options are
     * translated accordingly to the language used by the app at the moment
     * of creating an instance of MainMenu class.
     */
    private Map<String, Menu> prepareMenuOptions() {
        Map<String, Menu> options = new LinkedHashMap<>() {
            {
                put(
                        Localisation.get("main_menu.option.tables"),
                        new TablesMenu()
                );
                put(
                        Localisation.get("main_menu.option.db"),
                        new ManageDatabaseMenu()
                );
                put(
                        Localisation.get("main_menu.option.settings"),
                        new SettingsMenu()
                );
                put(
                        Localisation.get("main_menu.option.exit"),
                        new ExitMenu()
                );
            }
        };

        return Collections.unmodifiableMap(options);
    }

    /**
     * Prepares an instance of {@link OptionNumberReader} class with
     * localised menu options to be set as the value of MainMenu's reader
     * field.
     * @return the OptionNumberReader object with available menu options. All
     * of them are translated accordingly to the language used by the app at
     * the moment of creating an instance of MainMenu class.
     */
    private OptionNumberReader prepareReader() {
        String[] options = this.menuOptions.keySet().toArray(String[]::new);

        String message = Localisation.get("main_menu.message");

        return new OptionNumberReader(options, message);
    }

}
