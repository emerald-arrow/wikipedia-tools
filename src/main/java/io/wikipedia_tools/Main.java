package io.wikipedia_tools;

import io.wikipedia_tools.configs.AppContext;
import io.wikipedia_tools.configs.Localisation;
import io.wikipedia_tools.menus.impl.MainMenu;

import java.sql.SQLException;

/**
 * The class that starts the app.
 */
public class Main {

    /**
     * The method that stars the app. Initiates {@link AppContext} and
     * {@link Localisation} and starts {@link MainMenu}.
     * @param args a {@link String} array of arguments.
     */
    public static void main(String[] args) {
        try {
            AppContext.init();
        } catch (SQLException e) {
            System.out.println(e.getMessage());
            return;
        } catch (IllegalArgumentException e) {
            System.out.println("Critical error: " + e.getMessage());
            return;
        }

        Localisation.init(AppContext.getCurrentLanguage());

        new MainMenu().start();
    }
}