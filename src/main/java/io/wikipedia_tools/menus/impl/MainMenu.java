package io.wikipedia_tools.menus.impl;

import io.wikipedia_tools.configs.AppContext;
import io.wikipedia_tools.configs.Localisation;
import io.wikipedia_tools.menus.Menu;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Class for the first menu shown to the user.
 */
public class MainMenu implements Menu {
    private final Map<String, Menu> menuOptions;

    {
        this.menuOptions = prepareMenuOptions();
    }

    /**
     * Starts the menu.
     */
    @Override
    public void start() {
        AppContext.printCurrentSettings();

        for (String s : menuOptions.keySet()) {
            System.out.println(s);
        }
    }

    /**
     * Prepares a {@link LinkedHashMap} of localised {@link Menu} options.
     * @return the LinkedHashMap of Menu options. All options are translated
     * accordingly to the language currently used by the app.
     */
    private Map<String, Menu> prepareMenuOptions() {
        return new LinkedHashMap<>() {
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
    }
}
