package io.wikipedia_tools.menus.impl;

import io.wikipedia_tools.configs.AppContext;
import io.wikipedia_tools.configs.Localisation;
import io.wikipedia_tools.menus.Menu;
import io.wikipedia_tools.utils.readers.InputReader;
import io.wikipedia_tools.utils.readers.impl.OptionNumberReader;

import java.io.IOException;

/**
 * Class for menu with app's options for user to adjust. Menu's options are
 * not stored as fields to avoid the StackOverflowError exception.
 */
public class SettingsMenu implements Menu {

    /**
     * Starts and runs the menu.
     */
    @Override
    public void start() {
        AppContext.printCurrentSettings();

        final InputReader<Integer> reader = prepareReader();

        final Menu nextmenu = chooseOption(reader);

        if (nextmenu != null) {
            nextmenu.start();
        } else {
            Localisation.get("settings_menu.redirect.fail");
            return;
        }
    }

    /**
     * Asks for user input.
     * @param reader an instance of a class that implements
     *               {@link InputReader} interface. It is used to read user
     *               input.
     * @return an instance of a class implementing {@link Menu} interface. It
     * is going to be used to redirect the user.
     */
    private Menu chooseOption(InputReader<Integer> reader) {
        final Integer chosenOption;

        try {
            chosenOption = reader.read();
        } catch (IOException e) {
            System.out.println(e.getLocalizedMessage());
            return new ExitMenu();
        }

        if (chosenOption != null) {
            return getNextMenu(prepareSettingsMenus(), chosenOption - 1);
        }

        return null;
    }

    /**
     * Prepares an array of available settings menus.
     * @return an array of objects whose classes implement {@link Menu}
     * interface. It is going to be used to redirect the user to the menu of
     * their choice.
     */
    private static Menu[] prepareSettingsMenus() {
        return new Menu[] {
                new SettingsLanguageMenu(),
                new SettingsWikipediaMenu(),
                new MainMenu(),
                new ExitMenu()
        };
    }

    /**
     * Returns an object whose class implements {@link InputReader} interface
     * that is used to read user's input regarding what menu will be shown
     * next.
     * @return an instance of the {@link OptionNumberReader}. It is going to
     * be used to read user input.
     */
    private InputReader<Integer> prepareReader() {
        final String[] options = new String[] {
                Localisation.get("settings_menu.lang"),
                Localisation.get("settings_menu.wikipedia"),
                Localisation.get("settings_menu.back"),
                Localisation.get("settings_menu.exit")
        };

        return new OptionNumberReader(
                options,
                Localisation.get("settings_menu.msg")
        );
    }

    /**
     * Returns the {@link Menu} to which the user should be redirected into.
     * @param menus an array of objects whose classes implement Menu
     *              interface.
     * @param index an int used to retrieve next menu.
     * @return an object of a class that implements Menu interface where the
     * user will be redirected into.
     */
    private Menu getNextMenu(Menu[] menus, int index) {
        if (index < 0 || index > menus.length) {
            throw new IllegalArgumentException(
                    "Index must be a positive number and must not be" +
                            "greater than array's length"
            );
        }
        return menus[index];
    }
}
