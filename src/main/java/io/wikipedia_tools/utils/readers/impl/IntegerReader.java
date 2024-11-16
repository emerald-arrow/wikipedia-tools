package io.wikipedia_tools.utils.readers.impl;

import io.wikipedia_tools.configs.Localisation;
import io.wikipedia_tools.utils.readers.InputReader;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

/**
 * Class for reading an {@link Integer} from user input.
 */
public final class IntegerReader implements InputReader<Integer> {
    private Integer minValue;
    private Integer maxValue;
    private String message;

    /**
     * The constructor is private. Objects of this class are created by the
     * builder.
     */
    private IntegerReader() {}

    /**
     * Reads an {@link Integer} from user input.
     * @return the Integer provided by user.
     * @throws IOException when an error occurs while reading from system
     * input.
     * @throws NumberFormatException when user input cannot be parsed into
     * the Integer.
     */
    @Override
    public Integer read() throws IOException {
        printMessage();

        BufferedReader reader = new BufferedReader(
                new InputStreamReader(System.in)
        );

        int number;

        try {
            System.out.printf(
                    "%s: ", Localisation.get("integer_reader.number")
            );
            number = Integer.parseInt(reader.readLine().strip());
        } catch (NumberFormatException e) {
            throw new NumberFormatException(
                    Localisation.get(
                            "integer_reader.exception.number_format"
                    )
            );
        } catch (IOException e) {
            throw new IOException(e.getCause());
        }

        if (this.minValue != null && number < this.minValue) {
            System.out.printf(
                    "\n%s %d\n",
                    Localisation.get("integer_reader.error.too_small"),
                    this.minValue
            );
            return null;
        }

        if (this.maxValue != null && number > this.maxValue) {
            System.out.printf(
                    "\n%s %d\n",
                    Localisation.get("integer_reader.error.too_big"),
                    this.maxValue
            );
            return null;
        }

        return number;
    }

    /**
     * Prints the message to the user if message is not null.
     */
    private void printMessage() {
        if (this.message != null) {
            System.out.printf("\n%s\n", this.message);
        }
    }

    /**
     * Starts building an object of ReadInteger class.
     * @return a Builder that creates the object of ReadInteger class.
     */
    public static Builder builder() {
        return new Builder();
    }

    /**
     * Class that builds an object of ReadInteger class.
     */
    public static final class Builder {
        private Integer minValue;
        private Integer maxValue;
        private String message;

        /**
         * Sets the smallest accepted value of user input.
         * @param minValue an int that will be the smallest accepted number.
         * @return the Builder with arguments provided so far.
         */
        public Builder minValue(int minValue) {
            this.minValue = minValue;
            return this;
        }

        /**
         * Sets the highest accepted value of user input.
         * @param maxValue an int that will be the highest accepted number.
         * @return the Builder with arguments provided so far.
         */
        public Builder maxValue(int maxValue) {
            this.maxValue = maxValue;
            return this;
        }

        /**
         * Sets the information about what should be entered by the user.
         * @param message a String with text shown to the user.
         * @return the Builder with arguments provided so far.
         * @throws IllegalArgumentException when message is blank. Message
         * does not need to be set, but when it is set it must not be
         * blank.
         */
        public Builder message(String message) {
            if (this.message != null && this.message.isBlank()) {
                throw new IllegalArgumentException(
                        "If message is specified then it must not be blank."
                );
            }

            this.message = message;
            return this;
        }

        /**
         * Creates the object of ReadInteger class based on provided
         * arguments.
         * @return the object of ReadInteger class.
         */
        public IntegerReader build() {
            IntegerReader readInteger = new IntegerReader();
            readInteger.maxValue = this.maxValue;
            readInteger.minValue = this.minValue;
            readInteger.message = this.message;
            return readInteger;
        }
    }
}
