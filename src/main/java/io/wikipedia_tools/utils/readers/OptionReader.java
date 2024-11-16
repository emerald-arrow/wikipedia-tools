package io.wikipedia_tools.utils.readers;

/**
 * Abstract class for reading user input based on provided array of options.
 * @param <T>
 */
public abstract class OptionReader<T> implements InputReader<T> {

    /**
     * Prints available options.
     */
    protected abstract void printOptions();
}
