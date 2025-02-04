package io.wikipedia_tools.enums;

/**
 * Enum for sessions of race weekends.
 */
public enum Session {
    QUALIFYING,
    RACE;

    /**
     * Returns a {@code Session} based on given {@code String}.
     * @param text a String that contains a text to parse into a Session.
     * @return the Session that matches given String.
     * @throws IllegalArgumentException when given String is null, blank or
     * does not match any Session.
     */
    public static Session fromString(String text) {
        if (text == null || text.isBlank()) {
            throw new IllegalArgumentException(
                    "Given text must be neither null nor blank."
            );
        }

        for (Session session : Session.values()) {
            if (session.name().equalsIgnoreCase(text)) {
                return session;
            }
        }

        throw new IllegalArgumentException(
                "Given text does not match any session."
        );
    }
}
