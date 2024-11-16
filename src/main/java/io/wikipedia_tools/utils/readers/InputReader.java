package io.wikipedia_tools.utils.readers;

import java.io.IOException;

/**
 * Interface for reading rada from user's input.
 * @param <T> a type of returned value.
 */
public interface InputReader<T> {

    /**
     * Reads data from user's input.
     * @return data of T type.
     */
    T read() throws IOException;
}
