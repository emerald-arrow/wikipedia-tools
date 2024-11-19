package io.wikipedia_tools.menus.impl;

import io.wikipedia_tools.configs.AppContext;
import io.wikipedia_tools.configs.Localisation;
import io.wikipedia_tools.enums.WikipediaVersion;
import io.wikipedia_tools.menus.Menu;
import io.wikipedia_tools.utils.readers.InputReader;
import io.wikipedia_tools.utils.readers.impl.OptionNumberReader;

import java.io.IOException;

/**
 * Class that allows changing app's Wikipedia version.
 */
public class SettingsWikipediaMenu implements Menu {
    private final String[] options;
    private final InputReader<Integer> reader;

    /**
     * The constructor that does not take any arguments. All values of class'
     * fields are set without external arguments.
     */
    public SettingsWikipediaMenu() {
        this.options = prepareOptions();
        this.reader = prepareReader();
    }

    /**
     * Starts and runs the menu.
     */
    @Override
    public void start() {
        if (changeVersion()) {
            System.out.println(Localisation.get("menu_wikipedia.success"));
            new SettingsMenu().start();
        } else {
            System.out.println(Localisation.get("menu_wikipedia.fail"));
            new MainMenu().start();
        }
    }

    /**
     * Asks for user input and changes Wikipedia version used by the app.
     * @return a boolean - true when the changes of Wikipedia version is
     * successful, false when it fails.
     */
    private boolean changeVersion() {
        Integer chosenOption;

        try {
            chosenOption = this.reader.read();
        } catch (IOException e) {
            System.out.println(e.getLocalizedMessage());
            return false;
        }

        if (chosenOption == null) {
            return false;
        }

        WikipediaVersion version = WikipediaVersion.fromString(
                options[chosenOption - 1]
        );

        return AppContext.changeWikiVersion(version);
    }

    /**
     * Prepares an array with available Wikipedia versions' names.
     * @return the {@link String} array with names of available Wikipedia
     * versions.
     */
    private String[] prepareOptions() {
        return new String[] {
                WikipediaVersion.ENWIKI.name(),
                WikipediaVersion.PLWIKI.name()
        };
    }

    /**
     * Prepares an instance of a class that implements {@link InputReader}
     * interface. The instance features available Wikipedia versions and a
     * massage that is going to be shown to the user.
     * @return an instance of the {@link OptionNumberReader} class with
     * available Wikipedia versions names as options and a localised
     * information for the user as message.
     */
    private InputReader<Integer> prepareReader() {
        return new OptionNumberReader(
                this.options,
                Localisation.get("menu_wikipedia.msg")
        );
    }
}
