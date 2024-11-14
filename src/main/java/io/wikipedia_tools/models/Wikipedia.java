package io.wikipedia_tools.models;

import java.util.Objects;

/**
 * Class that stores data about Wikipedia versions retrieved from the
 * database.
 */
public class Wikipedia {
    private final int id;
    private final String name;

    /**
     * The constructor of the Wikipedia object.
     * @param id an {@link Integer} with Wikipedia's id in the database. The
     *           id must be greater than 0.
     * @param name a {@link String} with Wikipedia's name in the database.
     */
    public Wikipedia(Integer id, String name) {
        if (id == null) {
            throw new IllegalArgumentException("Id must not be null.");
        }

        if (id <= 0) {
            throw new IllegalArgumentException("Id must be greater than 0.");
        }

        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException(
                    "Name must neither be null or blank."
            );
        }

        this.id = id;
        this.name = name;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Wikipedia wikipedia)) return false;
        return id == wikipedia.id && Objects.equals(name, wikipedia.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name);
    }

    @Override
    public String toString() {
        return "Wikipedia{id=%d, name='%s'}".formatted(id, name);
    }
}
