package io.wikipedia_tools.enums;

/**
 * Enum for types of classifications.
 */
public enum ClassificationType {
    DRIVERS,
    MANUFACTURERS,
    TEAMS;

    /**
     * Returns a {@code ClassificationType} based on given {@code String}.
     * @param s a String that contains a text to parse into a
     *          ClassificationType.
     * @return a ClassificationType that matches given String.
     * @throws IllegalArgumentException - if given String is null, blank or
     * does not match any ClassificationType.
     */
    public static ClassificationType fromString(String s) {
        if (s == null || s.isBlank()) {
            throw new IllegalArgumentException(
                    "Given String must be neither null nor blank."
            );
        }

        for (ClassificationType type : ClassificationType.values()) {
            if (s.equalsIgnoreCase(type.name())) {
                return type;
            }
        }

        throw new IllegalArgumentException(
                "Given String does not match any ClassificationType."
        );
    }
}
