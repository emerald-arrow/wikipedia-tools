package io.wikipedia_tools.utils.readers.impl;

import io.wikipedia_tools.configs.Localisation;
import io.wikipedia_tools.utils.readers.InputReader;
import io.wikipedia_tools.utils.readers.OptionReader;

import java.io.IOException;

/**
 * Class for reading an {@link Integer} of the option chosen from user input.
 * A list of available options is shown to the user, and they choose the
 * integer attributed to the option.
 */
public class OptionNumberReader extends OptionReader<Integer> {
    private final String[] options;
    private final String message;

    public OptionNumberReader(String[] options, String message) {
        if (options.length >= 2) {
            this.options = options;
            this.message = message;
        } else {
            throw new IllegalArgumentException(
                    Localisation.get("option_number_reader.constructor.ex")
            );
        }
    }

    /**
     * Shows list of available options and asks the user for the number
     * attributed to one of them. Asking for user input is looped as long as
     * user's input does not meet requirements.
     * @return the Integer of the option chosen by the user. It is not an
     * index of that option in the array.
     * @throws IOException when an error occurs while reading from System
     * input.
     */
    @Override
    public Integer read() throws IOException {
        InputReader<Integer> reader = IntegerReader.builder()
                .minValue(1)
                .maxValue(options.length)
                .build();

        Integer number = null;

        while (number == null) {
            System.out.println(this.message);

            printOptions();

            try {
                number = reader.read();
            } catch (NumberFormatException e) {
                System.out.println(e.getLocalizedMessage());
            } catch (IOException e) {
                throw new IOException(e.getCause());
            }
        }

        return number;
    }

    /**
     * Prints available options.
     */
    @Override
    protected void printOptions() {
        for (int i = 1; i <= options.length; i++) {
            System.out.printf("%d. %s\n", i, options[i - 1]);
        }
    }
}
